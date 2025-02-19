# Generated by Django 5.1.4 on 2025-01-21 05:31

import django.contrib.auth.models
import django.db.models.deletion
import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('core.customuser',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='CustomerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('address_line_1', models.TextField(blank=True, null=True)),
                ('address_line_2', models.TextField(blank=True, null=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('city', models.TextField(blank=True, null=True)),
                ('state', models.TextField(blank=True, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('zip_code', models.TextField(blank=True, null=True)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='customer_profiles/')),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='customer.customer')),
            ],
        ),
    ]
