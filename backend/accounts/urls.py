from django.urls import path
from .views import UserRegistrationView,UserDetails,LoginView
from . views import *
from . import views
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('current-user/', UserDetails.as_view(),name='current-user'),
    path('update-user/', UpdateUserView.as_view(), name='update_user'),
]
