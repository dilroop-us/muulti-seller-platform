# Generated by Django 5.1.4 on 2025-02-07 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0009_alter_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('canceled', 'Canceled'), ('refunded', 'Refunded')], default='pending', max_length=20),
        ),
    ]
