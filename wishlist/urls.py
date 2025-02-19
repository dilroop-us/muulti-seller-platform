from django.urls import path
from .views import view_wishlist, add_to_wishlist, remove_from_wishlist, clear_wishlist, toggle_wishlist

app_name = 'wishlist'

urlpatterns = [
    path("", view_wishlist, name="wishlist"),
    path("toggle/<int:product_id>/", toggle_wishlist, name="toggle_wishlist"),
    path("add/<int:product_id>/", add_to_wishlist, name="add_to_wishlist"),
    path("remove/<int:product_id>/", remove_from_wishlist, name="remove_from_wishlist"),
    path("clear/", clear_wishlist, name="clear_wishlist"),
]
