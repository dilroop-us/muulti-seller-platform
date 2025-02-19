from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Customer, CustomerProfile


@receiver(post_save, sender=Customer)
def create_customer_profile(sender, instance, created, **kwargs):
    """Ensure a CustomerProfile instance is created for every new Customer"""
    if created:
        CustomerProfile.objects.create(customer=instance)





