# Generated by Django 5.1.2 on 2024-11-12 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0008_remove_booking_end_date_remove_booking_start_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='start_date',
            field=models.DateField(null=True),
        ),
    ]
