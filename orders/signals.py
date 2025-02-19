from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem, OrderStatus
from django.db.models import Count

@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_product_sold_count(sender, instance, **kwargs):
    """Update product sold count whenever an OrderItem is added, updated, or deleted."""
    product = instance.product
    sold_count = OrderItem.objects.filter(
        product=product,
        order__status__in=[OrderStatus.PENDING, OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.DELIVERED]
    ).aggregate(total_sold=Count('id'))['total_sold'] or 0

    product.sold_count = sold_count
    product.save()



