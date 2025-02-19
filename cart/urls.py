from django.urls import path
from .views import (
    cart,
    add_to_cart_view,
    update_cart_view,
    remove_from_cart_view,
    cart_total_view
)

app_name = "cart"

urlpatterns = [
    path("", cart, name="cart"),
    path("add/<int:product_id>/", add_to_cart_view, name="add_to_cart"),
    path("update/<int:product_id>/<str:action>/", update_cart_view, name="update_cart_quantity"),
    path("remove/<int:product_id>/", remove_from_cart_view, name="remove_from_cart"),
    path("total/", cart_total_view, name="cart_total"),
]
