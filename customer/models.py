from django.db import models
from core.models import CustomUser  # Assuming CustomUser is in core app
from django_countries.fields import CountryField



class Customer(CustomUser):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        """Ensure role is always 'customer'."""
        self.role = "customer"
        super().save(*args, **kwargs)


class CustomerProfile(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=100)
    address_line_1 = models.TextField(blank=True, null=True)
    address_line_2 = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    zip_code = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to="customer_profiles/", blank=True, null=True)
    country = CountryField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.username}'s Profile"


