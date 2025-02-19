# Generated by Django 5.1.4 on 2025-01-31 15:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0003_alter_checkout_cart'),
        ('payment', '0006_alter_payment_checkout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='checkout',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment', to='checkout.checkout'),
        ),
    ]
