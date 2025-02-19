# Generated by Django 5.1.4 on 2025-02-04 06:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('discount_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')], max_length=10)),
                ('value', models.DecimalField(decimal_places=2, help_text='Discount value (either % or fixed amount)', max_digits=10)),
                ('valid_from', models.DateTimeField()),
                ('valid_to', models.DateTimeField()),
                ('usage_limit', models.PositiveIntegerField(default=1)),
                ('used_count', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerCoupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('used_at', models.DateTimeField(auto_now_add=True)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coupons.coupon')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.customer')),
            ],
            options={
                'unique_together': {('customer', 'coupon')},
            },
        ),
    ]
