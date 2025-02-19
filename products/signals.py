from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product

@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_featured_products(sender, instance, **kwargs):
    """Automatically updates the featured products list based on sales."""
    # Get the top 10 best-selling in-stock products
    top_selling_products = Product.objects.filter(is_available=True, stock__gt=0).order_by("-sold_count")[:10]

    # Reset all featured products first
    Product.objects.update(featured=False)

    # Mark the top 10 as featured
    Product.objects.filter(id__in=top_selling_products.values_list("id", flat=True)).update(featured=True)
