# Generated by Django 5.1.4 on 2025-01-30 10:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0002_checkout_is_completed_alter_checkout_cart'),
        ('payment', '0003_alter_payment_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='checkout',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment', to='checkout.checkout'),
        ),
    ]
