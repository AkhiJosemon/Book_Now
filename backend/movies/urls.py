from django.urls import path
from django.contrib import admin
from .   import views
from .views  import * # Import views from the current directory
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
   path('all_movies/',MovieListView.as_view(),name="all_movies"),
   path('booking/<str:movie_name>/', views.booking_page, name='booking_page'),
   path('get_theaters_and_showtimes/<str:movie_name>/', views.get_theaters_and_showtimes, name='get_theaters_and_showtimes'),
   path('ws/booking/', BookingView.as_view(), name='ws_booking'),
   path('book_ticket/',views.book_ticket,name="book_ticket"),
   path('get_booked_seats/<str:movie_name>/<str:theater>/<str:showtime>/<str:date>/', views.get_booked_seats, name='get_booked_seats'),
   path('ticket/<str:booking_id>/', views.get_ticket, name='get_ticket'),
   path('get_tickets/',GetTicket.as_view(),name='get_ticket')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)