from django.urls import path
from . import views

app_name = "checkout"

urlpatterns = [
    path("", views.checkout_view, name="checkout_view"),  # Checkout page
    path('addresses/', views.customer_addresses, name='customer_addresses'),
    path('addresses/add/', views.add_customer_address, name='add_customer_address'),
    path('addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),
]