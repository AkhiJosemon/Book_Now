# Generated by Django 5.1.2 on 2024-11-12 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0010_remove_booking_start_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='movie',
            name='start_date',
        ),
        migrations.AddField(
            model_name='showtime',
            name='end_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='showtime',
            name='start_date',
            field=models.DateField(null=True),
        ),
    ]
