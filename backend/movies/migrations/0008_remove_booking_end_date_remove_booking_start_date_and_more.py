# Generated by Django 5.1.2 on 2024-11-12 09:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0007_booking_end_date_booking_start_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='showtime',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='showtime',
            name='start_date',
        ),
    ]