# Generated by Django 5.2 on 2025-05-02 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Grocery_app', '0002_category_cimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(default='', max_length=100),
        ),
    ]
