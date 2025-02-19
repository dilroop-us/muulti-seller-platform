from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Category, Product, ProductImage, ProductCategory


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    """Admin configuration for nested categories using MPTT."""
    list_display = ('tree_actions', 'indented_title', 'slug')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)
    list_filter = ('parent',)



