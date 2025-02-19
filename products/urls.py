from django.urls import path
from .views import (
    create_product,
    create_category,
    seller_products_list,
    update_product,
    product_detail,
    delete_product,


)
app_name = 'products'

urlpatterns = [
    path("create-product/", create_product, name="create_product"),  # Sellers only
    path("create-category/", create_category, name="create_category"),  # Admin only
    path("my_products/", seller_products_list, name="seller_products"),
    path("product/update/<int:product_id>/", update_product, name="update_product"),
    path("product/<int:product_id>/", product_detail, name="product_detail"),
    path("product/<int:product_id>/delete/", delete_product, name="delete_product"),

]
