from django.db import models, transaction
from django.core.exceptions import ValidationError
from checkout.models import Checkout
from customer.models import Customer

class PaymentMethod(models.TextChoices):
    COD = "cod", "Cash on Delivery"
    STRIPE = "stripe", "Stripe"

class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    CANCELED = "canceled", "Canceled"
    REFUNDED = "refunded", "Refunded"


class Payment(models.Model):
    """Model to store payment details."""
    checkout = models.OneToOneField(
        Checkout, on_delete=models.SET_NULL, related_name="payment", null=True, blank=True  # ✅ Allows NULL
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="payments"
    )
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices)  # Ensure correct field name
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    transaction_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    charge_id = models.CharField(max_length=255, blank=True, null=True, help_text="Stripe Charge ID")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["transaction_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["transaction_id"],
                condition=models.Q(status=PaymentStatus.COMPLETED),
                name="unique_transaction_id_for_completed"
            ),
        ]

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Amount must be greater than zero.")

    def mark_as_completed(self, transaction_id):
        """Mark the payment as completed and clear cart and checkout."""
        self.status = PaymentStatus.COMPLETED
        self.transaction_id = transaction_id
        self.save()

        # Ensure cart and checkout are cleared after successful payment
        self.clear_cart_and_checkout()

    def mark_as_failed(self, error_message):
        """Mark payment as failed and store error message."""
        self.status = PaymentStatus.FAILED
        self.error_message = error_message
        self.save()

    def clear_cart_and_checkout(self):
        """Clears cart and checkout while keeping orders and payments intact."""
        checkout = self.checkout

        if checkout:
            cart = checkout.cart

            if cart:
                # Delete all cart items but keep the cart object itself
                cart.cartitem_set.all().delete()

                # Reset session ID (optional, if needed)
                cart.session_id = None
                cart.save()

            # Delete checkout record to prevent duplicate processing
            checkout.delete()

    def __str__(self):
        return f"Payment {self.id} - {self.status}"
