import json
from django.shortcuts import render
from rest_framework.views import APIView
from . serializers import *
from rest_framework.response import Response
from .models import *
from django.http import JsonResponse
from rest_framework.decorators import api_view,permission_classes
from django.http import JsonResponse
from decimal import Decimal
from datetime import datetime
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from .paypal_config import *
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import status

CustomUser = get_user_model()

class MovieListView(APIView):
    
    permission_classes = [IsAuthenticated]
     
    def get(self, request):
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

def booking_page(request, movie_name):
    try:
        # Get the movie by name
        movie = Movie.objects.get(name=movie_name)
        
        # Get theaters and showtimes related to the movie
        theaters = Theater.objects.filter(movie=movie).values_list('name', flat=True)
        showtimes = ShowTime.objects.filter(movie=movie).values_list('time', flat=True)

        # Render the booking page and pass movie data
        return render(request, 'booking_page.html', {
            'movie_name': movie_name,
            'theaters': list(theaters),
            'showtimes': list(showtimes),
        })

    except Movie.DoesNotExist:
        return JsonResponse({'error': 'Movie not found'}, status=404)
    

def get_theaters_and_showtimes(request, movie_name):
    try:
        # Get the movie by name
        movie = Movie.objects.get(name=movie_name)
        
        # Get theaters related to the movie
        theaters = movie.theaters.all().values_list('name', flat=True)
        
        # Get showtimes for the movie
        showtimes = ShowTime.objects.filter(movie=movie).values_list('show_time', flat=True)

        return JsonResponse({
            'theaters': list(theaters),
            'showtimes': list(showtimes)
        })

    except Movie.DoesNotExist:
        return JsonResponse({'error': 'Movie not found'}, status=404)
        

class BookingView(APIView):
    def post(self, request):
        # Example of extracting data from the POST request body
        movie_name = request.data.get('movie_name')
        theater_name = request.data.get('theater_name')
        show_time = request.data.get('show_time')

        try:
            # Check if the movie exists
            movie = Movie.objects.get(name=movie_name)

            # Check if the theater exists
            theater = Theater.objects.get(name=theater_name)

            # Check if the showtime exists for the movie and theater
            showtime = ShowTime.objects.get(movie=movie, theater=theater, show_time=show_time)

            # You can add logic here to process the booking, e.g., creating a booking record

            return JsonResponse({'message': 'Booking successful!'}, status=200)

        except Movie.DoesNotExist:
            return JsonResponse({'error': 'Movie not found'}, status=404)
        except Theater.DoesNotExist:
            return JsonResponse({'error': 'Theater not found'}, status=404)
        except ShowTime.DoesNotExist:
            return JsonResponse({'error': 'Showtime not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_ticket(request):
    if request.method == "POST":
        # Get the data from the request body
        data = json.loads(request.body)
        movie_name = data.get("movieName")
        theater_name = data.get("theater")
        showtime = data.get("showtime")
        seats = data.get("seats").split(", ")  # Convert comma-separated string to list of seats
        price = data.get("price")
        date_str = data.get("date")
        
        # Log the incoming data for debugging
        print("booked ticket")
        print(data)

        # Convert the date to a valid datetime object
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # Convert price to Decimal
        try:
            price = Decimal(price)
        except ValueError:
            return JsonResponse({"error": "Invalid price value."}, status=400)

        try:
            # Fetch movie, theater, and showtime from the database
            movie = Movie.objects.get(name=movie_name)
            theater = Theater.objects.get(name=theater_name)
            showtime_obj = ShowTime.objects.get(show_time=showtime, movie=movie, theater=theater)
            user = CustomUser.objects.get(id=request.user.id) 
            # Create a new booking
            booking = Booking.objects.create(
                user=user,
                movie=movie,
                theater=theater,
                showtime=showtime_obj,
                seats=", ".join(seats),  # Save as a comma-separated string
                price=price,
                date=date
            )

            # Return a success response with the booking ID
            return JsonResponse({"message": "Booking successful!", "booking_id": booking.id}, status=201)

        except Movie.DoesNotExist:
            return JsonResponse({"error": "Movie not found."}, status=404)
        except Theater.DoesNotExist:
            return JsonResponse({"error": "Theater not found."}, status=404)
        except ShowTime.DoesNotExist:
            return JsonResponse({"error": "Showtime not found."}, status=404)
        except Exception as e:
            # Log any unexpected errors
            print(f"Unexpected error: {e}")
            return JsonResponse({"error": "An error occurred. Please try again later."}, status=400)

def get_booked_seats(request, movie_name, theater, showtime, date):
    try:
        # Get movie and theater objects
        movie = Movie.objects.get(name=movie_name)
        theater_obj = Theater.objects.get(name=theater)
        
        # Fetch the showtime object by movie, theater, and showtime
        showtime_obj = ShowTime.objects.get(movie=movie, theater=theater_obj, show_time=showtime)

        # Ensure the date matches with the booking date, not the showtime's start date
        # We are using Booking's date field for filtering
        bookings = Booking.objects.filter(
            movie=movie,
            theater=theater_obj,
            showtime=showtime_obj,
            date=date  # Filter bookings by the date field in Booking model
        )

        booked_seats = []
        for booking in bookings:
            # Split the string and convert each seat to an integer
            seats = booking.seats.replace('[', '').replace(']', '').replace("'", '').split(',')
            booked_seats.extend(map(int, seats))

        return JsonResponse({'booked_seats': booked_seats}, status=200)

    except Movie.DoesNotExist:
        return JsonResponse({'error': 'Movie not found'}, status=400)
    except Theater.DoesNotExist:
        return JsonResponse({'error': 'Theater not found'}, status=400)
    except ShowTime.DoesNotExist:
        return JsonResponse({'error': 'Showtime not found'}, status=400)
    except ValueError as ve:
        return JsonResponse({'error': 'Invalid seat data format'}, status=400)




@api_view(['GET'])
def get_available_dates(request, movie_name, theater_name):
    try:
        movie = Movie.objects.get(name=movie_name)
        theater = Theater.objects.get(name=theater_name)
        
        showtimes = ShowTime.objects.filter(movie=movie, theater=theater)
        
        available_dates = []
        for showtime in showtimes:
            # Add available date range between start_date and end_date for each showtime
            available_dates.append({
                'start_date': showtime.start_date,
                'end_date': showtime.end_date
            })
        
        return JsonResponse({'available_dates': available_dates}, status=200)

    except Movie.DoesNotExist:
        return JsonResponse({'error': 'Movie not found'}, status=400)
    except Theater.DoesNotExist:
        return JsonResponse({'error': 'Theater not found'}, status=400)
    

# Configure PayPal SDK

# Create PayPal Payment
@api_view(['POST'])
def create_paypal_payment(request):
    data = request.data  # Get data from frontend (booking details)
    
    # Create a PayPal payment
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": str(data['price']),  # Total price
                "currency": "INR"  # Currency
            },
            "description": f"Booking for {data['movie_name']} at {data['theater_name']}"
        }],
        "redirect_urls": {
            "return_url": "http://localhost:8000/payment/success/",
            "cancel_url": "http://localhost:8000/payment/cancel/"
        }
    })

    # Create the payment
    if payment.create():
        # Store payment details in your database if necessary
        # You can also link the payment to the booking in your database
        booking = Booking.objects.create(
            movie_name=data['movie_name'],
            theater_name=data['theater_name'],
            price=data['price'],
            user=request.user  # Optional: associate payment with the user
        )

        # Find the approval URL to redirect the user to PayPal
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                return JsonResponse({"payment_url": approval_url}, status=200)

    else:
        return JsonResponse({"error": "Payment creation failed."}, status=400)

# Success URL: This will be hit after the user makes the payment.
@api_view(['GET'])
def payment_success(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    # Execute the payment
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        return JsonResponse({"message": "Payment successful!"}, status=200)
    else:
        return JsonResponse({"error": "Payment execution failed."}, status=400)

# Cancel URL: This will be hit if the user cancels the payment.
@api_view(['GET'])
def payment_cancel(request):
    return JsonResponse({"message": "Payment canceled."}, status=200)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_ticket(request, booking_id):
    try:
        # Retrieve the booking from the database using the booking_id
        ticket = Booking.objects.get(pk=booking_id)

        # Extract data from the ticket and related models
        ticket_data = {
            "customer_name": ticket.user.first_name,
            "movie_name": ticket.movie.name,  # Access the 'name' field of the related Movie model
            "event_name": ticket.theater.name,  # Access the 'name' field of the related Theater model
            "event_time": ticket.showtime.show_time.strftime('%H:%M:%S'),  # Formatting datetime to string
            "event_date": ticket.date.strftime('%Y-%m-%d'),  # Formatting date to string
            "event_seat": ticket.seats,
            "event_location": ticket.theater.name,  # Assuming you want the theater name again
        }

        return JsonResponse(ticket_data)

    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

class GetTicket(APIView):
     permission_classes = [IsAuthenticated]
     def get(self,request):
         user=request.user
         tickets=Booking.objects.filter(user=user)
         print(tickets)
         if not tickets.exists():
            return Response(
                {"message": "No tickets found for this user."}, 
                status=status.HTTP_404_NOT_FOUND
            )
         
         ticket_data = []
         for ticket in tickets:
            ticket_data.append({
                "Booking_id":ticket.id,
                "movie_name": ticket.movie.name,  # Assuming 'name' is a field in the Movie model
                "event_name": ticket.theater.name,  # Assuming 'name' is a field in the Theater model
                "event_time": ticket.showtime.show_time,  # Assuming 'show_time' is a field in the ShowTime model
                "event_date": ticket.date.strftime('%Y-%m-%d'),  # Formatting date
                "event_seat": ticket.seats,
                "event_location": ticket.theater.name,  # Assuming 'name' is a field in the Theater model
            })

        # If tickets found, return them with a 200 status
         return Response(ticket_data, status=status.HTTP_200_OK)

