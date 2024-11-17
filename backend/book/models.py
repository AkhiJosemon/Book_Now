from django.db import models
from datetime import date

class Booking(models.Model):
    movie_name = models.CharField(max_length=100)
    theater_name = models.CharField(max_length=100)
    seat_number = models.PositiveIntegerField()
    date = models.DateField(default=date.today,null=True) 
    time = models.TimeField()

    def __str__(self):
        return f"{self.movie_name} at {self.theater_name} (Seat {self.seat_number}) on {self.date} at {self.time}"
