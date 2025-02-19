from django.db.models.signals import post_save
from django.dispatch import receiver
from seller.models import Seller, SellerProfile, SellerStore
from django.conf import settings
import uuid
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY  # Set API key globally

@receiver(post_save, sender=Seller)
def create_seller_profile(sender, instance, created, **kwargs):
    """Automatically create a SellerProfile when a Seller is created."""
    if created and not SellerProfile.objects.filter(seller=instance).exists():
        SellerProfile.objects.create(seller=instance)


@receiver(post_save, sender=Seller)
def create_seller_store(sender, instance, created, **kwargs):
    """Automatically create a SellerStore when a Seller is created."""
    if created and not SellerStore.objects.filter(seller=instance).exists():
        unique_id = uuid.uuid4().hex[:8]  # Generate an 8-character unique ID
        store_name = f"{instance.first_name}'s Store-{unique_id}"  # Store name with UUID

        SellerStore.objects.create(
            seller=instance,
            store_name=store_name,
            owner_name=f"{instance.first_name} {instance.last_name}"
        )


@receiver(post_save, sender=SellerProfile)
def update_onboarding_status(sender, instance, created, **kwargs):
    """Automatically update is_onboarded when a Stripe account is created."""
    if instance.stripe_account_id:
        try:
            stripe_account = stripe.Account.retrieve(instance.stripe_account_id)
            if stripe_account.charges_enabled and stripe_account.payouts_enabled:
                instance.is_onboarded = True
                instance.save(update_fields=['is_onboarded'])
        except stripe.error.StripeError as e:
            print(f"Stripe API Error: {e}")