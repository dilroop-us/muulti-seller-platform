from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from django.core.validators import MinValueValidator, MaxValueValidator
from seller.models import SellerStore  # Linking products to stores


class Category(MPTTModel):
    """Hierarchical Category model using MPTT for nested structure."""

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, related_name="children", null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return " → ".join([ancestor.name for ancestor in self.get_ancestors(include_self=True)])


class Product(models.Model):
    """Product model linked to SellerStore, supporting multiple categories."""
    store = models.ForeignKey(SellerStore, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    sold_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    categories = models.ManyToManyField(Category, through='ProductCategory')

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_available']),
            models.Index(fields=['price']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        # Update availability based on stock
        if self.is_available is None:
            self.is_available = self.stock > 0

        # Only generate a new slug if it isn't already set
        if not self.slug:
            base_slug = slugify(self.name)
            slug_candidate = base_slug
            counter = 1

            # Keep incrementing until a unique slug is found
            while Product.objects.filter(slug=slug_candidate).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug_candidate

        super().save(*args, **kwargs)

    def get_discounted_price(self):
        """Returns the discounted price."""
        return round(self.price - (self.price * self.discount / 100), 2)

    def get_child_category(self):
        """Returns the first child category of the product."""
        return self.categories.filter(parent__isnull=False).first()

    def __str__(self):
        return f"{self.name} - {self.store.store_name}"


class ProductImage(models.Model):
    """Model to store multiple images for a product."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='product_images/%Y/%m/%d/')  # Changed from URLField to ImageField
    is_main = models.BooleanField(default=False)  # Mark if it's the primary image

    class Meta:
        ordering = ['-is_main']  # Ensure the main image appears first

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductCategory(models.Model):
    """Intermediate table for Many-to-Many relationship between Product and Category."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_categories')

    class Meta:
        unique_together = ('product', 'category')  # Prevent duplicate product-category relationships

    def __str__(self):
        return f"{self.product.name} - {self.category.name}"
