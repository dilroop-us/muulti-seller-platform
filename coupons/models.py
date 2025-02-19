# coupons/models
from django.db import models
from django.utils.timezone import now
from django.apps import apps
from customer.models import Customer
from django.db import transaction



class Coupon(models.Model):
    """Coupon model for applying discounts at checkout."""

    DISCOUNT_TYPES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )

    code = models.CharField(max_length=20, unique=True, db_index=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES)
    value = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Discount value (Percentage or Fixed Amount)"
    )
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=1, help_text="Maximum times this coupon can be used")
    used_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-valid_to']
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def is_valid(self):
        """Check if the coupon is valid based on time and usage."""
        current_time = now()
        return self.valid_from <= current_time <= self.valid_to and self.used_count < self.usage_limit

    @property
    def is_expired(self):
        """Returns True if the coupon has expired."""
        return now() > self.valid_to

    def apply_discount(self, total_price):
        """Applies the coupon discount to the total price, ensuring it doesn't go negative."""
        if not self.is_valid():
            return total_price  # No discount if coupon is invalid

        discount = (self.value / 100) * total_price if self.discount_type == 'percentage' else self.value
        return max(total_price - discount, 0)  # Ensure non-negative total

    def use_coupon(self):
        """Atomically increment used count"""
        if not self.is_valid():
            raise ValueError("This coupon is no longer valid.")

        with transaction.atomic():
            self.used_count = models.F('used_count') + 1  # Avoids race conditions
            self.save(update_fields=['used_count'])

    def __str__(self):
        return f"{self.code} - {self.get_discount_display()} (Used: {self.used_count}/{self.usage_limit})"




class CustomerCoupon(models.Model):
    """Tracks which customers have used a coupon to prevent multiple uses."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'coupon')  # Ensures one-time use per customer

    def __str__(self):
        return f"{self.customer.username} used {self.coupon.code}"
