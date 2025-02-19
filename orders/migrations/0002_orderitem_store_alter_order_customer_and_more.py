# Generated by Django 5.1.4 on 2025-01-31 04:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
        ('orders', '0001_initial'),
        ('payment', '0004_alter_payment_checkout'),
        ('seller', '0002_sellerprofile_is_onboarded_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='store',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='seller.sellerstore'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='customer.customer'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='order', to='payment.payment'),
        ),
    ]
