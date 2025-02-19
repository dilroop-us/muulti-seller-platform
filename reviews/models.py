from django.db import models
from products.models import Product
from customer.models import Customer



class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1 to 5 stars

    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_offensive = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.username} - {self.product.name} - {self.rating} Stars"
