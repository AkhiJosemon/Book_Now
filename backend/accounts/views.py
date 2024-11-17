from django.contrib.auth import authenticate
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework_simplejwt.authentication import JWTAuthentication

CustomUser = get_user_model()

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User created successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Extract email and password from request
            email = request.data['email']
            password = request.data['password']
        except KeyError:
            raise ParseError('All Fields Are Required')

        # Check if user exists
        if not CustomUser.objects.filter(email=email).exists():
            raise AuthenticationFailed('Invalid Email Address')

        # Check if user is active
        user = CustomUser.objects.get(email=email)
        if not user.is_active:
            raise AuthenticationFailed('You are blocked by admin! Please contact admin')

        # Authenticate the user using email and password
        user = authenticate(email=email, password=password)
        if user is None:
            raise AuthenticationFailed('Invalid Password')

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        refresh['user'] = user.id
        refresh["first_name"] = str(user.first_name)
        refresh['is_superuser'] = user.is_superuser
        refresh['email'] = user.email

        # Prepare response data
        content = {
            'user_id': user.id,
            'refresh_token': str(refresh),
            'access_access': str(refresh.access_token),
            'isAdmin': user.is_superuser,
        }
        return Response(content, status=status.HTTP_200_OK)


class UserDetails(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]  

    def get(self, request):
        user = request.user
        user_data = {
            "id": user.id,
            "username": user.email,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        return Response(user_data, status=status.HTTP_200_OK)


class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user  # Get the authenticated user
        
        # Ensure the request contains valid data
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        
        # Update user fields
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        
        # Save the updated user object
        user.save()

        data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
           
        }

        # Return the updated user details as response
        return Response(data, status=status.HTTP_200_OK)
