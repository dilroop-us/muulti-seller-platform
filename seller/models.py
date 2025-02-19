from django.db import models
from core.models import CustomUser
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class Seller(CustomUser):
    """Proxy model for sellers with additional seller-specific methods."""
    class Meta:
        proxy = True

    def get_store(self):
        """Return the associated store if exists."""
        return getattr(self.seller_profile, "store", None)


class SellerProfile(models.Model):
    """Seller Profile for storing additional seller information."""

    seller = models.OneToOneField(Seller, on_delete=models.CASCADE, related_name="seller_profile")
    profile_image = models.ImageField(upload_to='seller_profiles/%Y/%m/%d/', blank=True, null=True)
    phone_number = PhoneNumberField(region="US", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    is_onboarded = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of {self.seller.email}"


class SellerStore(models.Model):
    """Store details for sellers."""

    seller = models.OneToOneField(Seller, on_delete=models.CASCADE, related_name="store")
    # Store Information
    store_name = models.CharField(max_length=255, unique=True)
    store_logo = models.ImageField(upload_to='store_logos/%Y/%m/%d/', blank=True, null=True)
    store_address_line_1 = models.CharField(max_length=255, blank=True)
    store_address_line_2 = models.CharField(max_length=255, blank=True)
    store_city = models.CharField(max_length=100, blank=True)
    store_state = models.CharField(max_length=100, blank=True)
    store_country = CountryField(blank_label='Select country', blank=True)
    store_zip_code = models.CharField(max_length=10, blank=True)
    # Owner Information
    owner_name = models.CharField(max_length=255)
    phone_number = PhoneNumberField(region="US", blank=True, null=True)
    # Business Verification
    tax_id = models.CharField(max_length=15, unique=True, blank=True, null=True)
    # Optional Financial Information
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(blank=True, null=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Store: {self.store_name} ({self.seller.email})"
