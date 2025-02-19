from django.db import models
from django_countries.fields import CountryField
from django.core.validators import RegexValidator, MinValueValidator
from products.models import Product
from cart.models import Cart
from customer.models import Customer
from django.utils.timezone import now
from coupons.models import Coupon, CustomerCoupon
from decimal import Decimal

class ShippingAddress(models.Model):
    """Model to store customer shipping addresses."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="shipping_addresses")
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True, default='')
    address_line_2 = models.CharField(max_length=255, blank=True, null=True, default='')
    city = models.CharField(max_length=100, blank=True, null=True, default='')
    state = models.CharField(max_length=100, blank=True, null=True, default='')
    zip_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{5}(-\d{4})?$', message="Zip code must be entered in the format: '12345' or '12345-6789'.")]
    )
    country = CountryField(blank_label='Select Country')

    def __str__(self):
        return f"{self.customer.username} - {self.address_line_1}"


class Checkout(models.Model):
    """Stores checkout data before finalizing an order."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="checkouts")
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey("ShippingAddress", on_delete=models.SET_NULL, null=True)
    coupon = models.ForeignKey("coupons.Coupon", on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)]
    )
    payment_method = models.CharField(
        max_length=20,
        choices=(('stripe', 'Stripe'), ('cod', 'Cash on Delivery'))
    )
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def apply_coupon(self, coupon_code):
        """Applies a coupon, updates the discounted total price, and saves the checkout."""
        from coupons.utils import apply_coupon

        result = apply_coupon(self.customer, coupon_code, self.total_price)
        if result["success"]:
            self.coupon = result["coupon"]
            self.total_price = result["new_total"]  # Update total price after discount
            self.save()
        return result

    @property
    def coupon_discount(self):
        """Returns the discount amount applied by the coupon."""
        if self.coupon and self.coupon.is_valid():
            return self.coupon.apply_discount(self.total_price)
        return Decimal("0.00")

    @property
    def discounted_total_price(self):
        """Returns the total price after applying the coupon."""
        return max(self.total_price - self.coupon_discount, Decimal("0.00"))

    def __str__(self):
        return f"Checkout #{self.id} - {self.customer.username}"
