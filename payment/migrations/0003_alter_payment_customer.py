# Generated by Django 5.1.4 on 2025-01-29 06:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
        ('payment', '0002_alter_payment_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='customer.customer'),
        ),
    ]
