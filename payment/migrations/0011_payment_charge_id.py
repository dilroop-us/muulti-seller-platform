# Generated by Django 5.1.4 on 2025-02-07 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0010_alter_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='charge_id',
            field=models.CharField(blank=True, help_text='Stripe Charge ID', max_length=255, null=True),
        ),
    ]
