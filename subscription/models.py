import stripe
from django.conf import settings
from django.db import models
from datetime import timedelta
from django.utils import timezone  # Import Django's timezone
from seller.models import SellerProfile

stripe.api_key = settings.STRIPE_SECRET_KEY

class Subscription(models.Model):
    """Subscription model linked to SellerProfile"""

    seller_profile = models.OneToOneField(
        SellerProfile, on_delete=models.CASCADE, related_name="subscription"
    )
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("active", "Active"),
            ("expired", "Expired"),
        ],
        default="pending",
    )
    start_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    def activate_subscription(self):
        """Activate subscription for one year."""
        self.status = "active"
        self.expiry_date = timezone.now() + timedelta(days=365)
        self.save()

    def is_active(self):
        """Check if subscription is active."""
        return (
            self.status == "active"
            and self.expiry_date is not None
            and self.expiry_date > timezone.now()
        )

    def __str__(self):
        return f"Subscription for {self.seller_profile.seller.email} - {self.status}"
