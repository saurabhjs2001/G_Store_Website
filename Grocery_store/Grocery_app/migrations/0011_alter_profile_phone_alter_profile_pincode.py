# Generated by Django 5.2 on 2025-05-17 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Grocery_app', '0010_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='phone',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='profile',
            name='pincode',
            field=models.CharField(max_length=6),
        ),
    ]
