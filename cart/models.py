# Cart/models.py
from django.db import models
from django_countries.fields import CountryField
from django.core.validators import RegexValidator, MinValueValidator
from products.models import Product
from customer.models import Customer
import uuid
from django.db.models import Sum, F, ExpressionWrapper, DecimalField


class Cart(models.Model):
    """Cart model to store customer-selected products before checkout."""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name="cart")
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.customer.username if self.customer else f'Guest {self.session_id}'}"

    def get_total_price(self):
        """Calculate total cart price before discounts."""
        return self.cartitem_set.aggregate(
            total=Sum(ExpressionWrapper(
                F("quantity") * F("product__price"),
                output_field=DecimalField()
            ))
        )["total"] or 0

    def get_subtotal(self):
        """Calculate subtotal after applying product discounts."""
        return self.cartitem_set.aggregate(
            subtotal=Sum(ExpressionWrapper(
                F("quantity") * (F("product__price") - (F("product__price") * (F("product__discount") / 100))),
                output_field=DecimalField()
            ))
        )["subtotal"] or 0


class CartItem(models.Model):
    """Model for individual cart items."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1, message="Quantity must be at least 1")]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_discounted_price(self):
        """Calculate the discounted price per item."""
        return self.product.price - (self.product.price * (self.product.discount / 100))

    def get_total_price(self):
        """Calculate total price for the cart item."""
        return self.get_discounted_price() * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart"

    class Meta:
        unique_together = ('cart', 'product')
