from django.db import models
from django.utils import timezone
from accounts.models import *
from django.contrib.auth import get_user_model 
from django.conf import settings

User = get_user_model()  

class Theater(models.Model):
    THEATER_CHOICES = [
        ('EVM', 'EVM'),
        ('PVR', 'PVR'),
        ('CINEPOLIS', 'CINEPOLIS'),
        ('G CINEMAS', 'G CINEMAS'),
        ('M CINEMAS', 'M CINEMAS'),
        ('K CINEMAS', 'K CINEMAS'),
    ]

    name = models.CharField(max_length=100, choices=THEATER_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    LANGUAGE_CHOICES = [
        ('ENGLISH', 'English'),
        ('MALAYALAM', 'Malayalam'),
        ('HINDI', 'Hindi'),
        ('TAMIL', 'Tamil'),
    ]

    CATEGORY_CHOICES = [
        ('ACTION', 'Action'),
        ('THRILLER', 'Thriller'),
        ('COMEDY', 'Comedy'),
        ('ROMANTIC', 'Romantic'),
    ]

    name = models.CharField(max_length=255)
    director = models.CharField(max_length=255)
    cast = models.TextField(help_text="Enter cast names separated by commas")  # Stores cast names as a comma-separated string
    poster = models.ImageField(upload_to='posters/')  # Requires Pillow for image handling
    language = models.CharField(max_length=255, choices=LANGUAGE_CHOICES)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    theaters = models.ManyToManyField(Theater, related_name='movies')  # Allows multiple theater selections
    

    def __str__(self):
        return self.name

    def get_cast_list(self):
        """Returns the cast as a list of names."""
        return [cast_name.strip() for cast_name in self.cast.split(',')]

    def get_theater_names(self):
        """Returns a list of theater names for this movie."""
        return [theater.name for theater in self.theaters.all()]


class ShowTime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="showtimes")
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name="showtimes")
    show_time = models.TimeField()
    start_date = models.DateField(null=True)  # Start date for showtimes
    end_date = models.DateField(null=True) 
    
    
    def __str__(self):
        return f"{self.movie.name} at {self.theater.name} on {self.show_time}"

    class Meta:
        unique_together = ('movie', 'theater', 'show_time')  

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    showtime = models.ForeignKey(ShowTime, on_delete=models.CASCADE)
    seats = models.TextField()  # Store selected seat numbers as a string
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    date = models.DateField()

    def __str__(self):
        return f"Booking for {self.movie.name} at {self.theater.name} - {self.showtime.show_time}"
from django.contrib.auth.models import User



class Ticket(models.Model):
    booking_id = models.CharField(max_length=255, unique=True)
    customer_name = models.CharField(max_length=255)
    event_name = models.CharField(max_length=255)
    event_date = models.DateTimeField(null=True)
    event_location = models.CharField(max_length=255)

    def __str__(self):
        return f"Ticket for {self.customer_name} - {self.event_name} on {self.event_date}"