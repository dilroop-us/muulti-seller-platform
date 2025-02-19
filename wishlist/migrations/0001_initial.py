# Generated by Django 5.1.4 on 2025-01-28 05:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlists', to='customer.customerprofile')),
                ('products', models.ManyToManyField(related_name='wishlisted_by', to='products.product')),
            ],
        ),
    ]
