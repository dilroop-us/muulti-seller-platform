from django.db import models
from products.models import Product
from customer.models import CustomerProfile
import redis
from django.conf import settings

# Redis connection
redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)


class Wishlist(models.Model):
    customer_profile = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="wishlists",
    )
    products = models.ManyToManyField(Product, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_profile.customer.email}'s Wishlist"

    def save_to_cache(self):
        """Cache customer's wishlist in Redis"""
        key = f"wishlist:{self.customer_profile.customer.email}"
        product_ids = list(self.products.values_list('id', flat=True))
        redis_client.set(key, ",".join(map(str, product_ids)))
        redis_client.expire(key, 3600)

    @classmethod
    def get_cached_wishlist(cls, customer_email):
        """Retrieve wishlist from cache"""
        key = f"wishlist:{customer_email}"
        product_ids = redis_client.get(key)
        return product_ids.split(",") if product_ids else None
