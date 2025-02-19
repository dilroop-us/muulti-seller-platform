from django.db import models, transaction
from django.core.validators import MinValueValidator
from checkout.models import Checkout, ShippingAddress
from customer.models import Customer
from products.models import Product
from payment.models import Payment
from seller.models import SellerStore
from django.conf import settings
import stripe
import uuid
from django.db.models import Count


stripe.api_key = settings.STRIPE_SECRET_KEY


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    SHIPPED = "shipped", "Shipped"
    DELIVERED = "delivered", "Delivered"
    CANCELED = "canceled", "Canceled"
    REFUNDED = "refunded", "Refunded"


class OrderItemStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    SHIPPED = "shipped", "Shipped"
    DELIVERED = "delivered", "Delivered"
    CANCELED = "canceled", "Canceled"
    REFUNDED = "refunded", "Refunded"


class StoreOrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    SHIPPED = "shipped", "Shipped"
    COMPLETED = "completed", "Completed"
    CANCELED = "canceled", "Canceled"
    REFUNDED = "refunded", "Refunded"

class PaymentMethod(models.TextChoices):
    COD = "cod", "Cash on Delivery"
    STRIPE = "stripe", "Stripe"


class Order(models.Model):
    """Stores successful orders after payment is completed."""
    order_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders", db_index=True)
    payment = models.OneToOneField(Payment, on_delete=models.PROTECT, related_name="order")
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.COD)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.PROTECT, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['customer', 'created_at']),
        ]

    def __str__(self):
        return f"Order #{self.order_uuid} - {self.customer.username} - {self.status}"

    def get_full_shipping_address(self):
        """Returns a formatted shipping address from the ShippingAddress model."""
        return (
            f"{self.shipping_address.full_name}\n"
            f"{self.shipping_address.address_line_1}, {self.shipping_address.address_line_2}\n"
            f"{self.shipping_address.city}, {self.shipping_address.state} {self.shipping_address.zip_code}\n"
            f"{self.shipping_address.country.name}\n"
            f"Phone: {self.shipping_address.phone}"
        )

    def update_order_status(self):
        """Updates the overall order status based on the statuses of its items."""
        item_statuses = self.items.values_list("status", flat=True)

        if all(status == OrderItemStatus.CANCELED for status in item_statuses):
            self.status = OrderStatus.CANCELED
        elif all(status == OrderItemStatus.DELIVERED for status in item_statuses):
            self.status = OrderStatus.DELIVERED
        elif all(status == OrderItemStatus.SHIPPED for status in item_statuses):
            self.status = OrderStatus.SHIPPED
        elif all(status == OrderItemStatus.PROCESSING for status in item_statuses):
            self.status = OrderStatus.PROCESSING
        else:
            self.status = OrderStatus.PENDING

        self.save()



class OrderItem(models.Model):
    """Stores products associated with an order, allowing per-product status updates."""
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(SellerStore, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=OrderItemStatus.choices, default=OrderItemStatus.PENDING)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} from {self.store.name} in Order #{self.order.id}"

    def update_status(self, new_status):
        """Updates the status of an order item and triggers necessary order updates."""
        self.status = new_status
        self.save()
        self.order.update_order_status()

        # Update the store's order status
        store_order = self.order.store_orders.filter(store=self.store).first()
        if store_order:
            store_order.update_status()

    def cancel_item(self):
        """Cancels a single order item and updates sold count and order status."""
        if self.status in [OrderItemStatus.CANCELED, OrderItemStatus.REFUNDED]:
            return False  # Already canceled

        with transaction.atomic():  # Ensures database consistency
            self.status = OrderItemStatus.CANCELED
            self.save()

            # Reduce sold count only if it's a cancellation
            self.update_sold_count(decrease=True)

            # Update order and store statuses
            self.order.update_order_status()

            store_order = self.order.store_orders.filter(store=self.store).first()
            if store_order:
                store_order.update_status()

        return True

    def update_sold_count(self, decrease=False):
        """Updates the sold count when an order item is canceled or purchased."""
        if decrease:
            # Recalculate sold count only for non-canceled and non-refunded orders
            sold_count = OrderItem.objects.filter(
                product=self.product,
                order__status__in=[OrderStatus.PENDING, OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.DELIVERED]
            ).aggregate(total_sold=Count('id'))['total_sold'] or 0

            # Update product's sold count
            self.product.sold_count = sold_count
            self.product.save()

            # Trigger automatic update of featured products via signals
            self.trigger_featured_update()

    def trigger_featured_update(self):
        """Trigger automatic featured product selection when sales change."""
        from products.signals import update_featured_products  # Import dynamically to avoid circular imports
        update_featured_products(sender=Product, instance=self.product)


class StoreOrder(models.Model):
    """
    Tracks order status for a particular store.
    If an order contains multiple stores, each store will have its own status.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="store_orders")
    store = models.ForeignKey(SellerStore, on_delete=models.CASCADE, related_name="store_orders")
    status = models.CharField(max_length=20, choices=StoreOrderStatus.choices, default=StoreOrderStatus.PENDING)

    def update_status(self):
        """
        Updates the store order status based on the individual OrderItems for this store.
        """
        order_items = self.order.items.filter(store=self.store)
        item_statuses = order_items.values_list("status", flat=True)

        if all(status == OrderItemStatus.CANCELED for status in item_statuses):
            self.status = StoreOrderStatus.CANCELED
        elif all(status == OrderItemStatus.DELIVERED for status in item_statuses):
            self.status = StoreOrderStatus.COMPLETED
        elif all(status == OrderItemStatus.SHIPPED for status in item_statuses):
            self.status = StoreOrderStatus.SHIPPED
        elif all(status == OrderItemStatus.PROCESSING for status in item_statuses):
            self.status = StoreOrderStatus.PROCESSING
        else:
            self.status = StoreOrderStatus.PENDING

        self.save()

