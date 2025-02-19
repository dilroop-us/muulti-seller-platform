from django.urls import path
from .views import stripe_seller_webhook, stripe_connect_page

app_name = 'seller_payments'

urlpatterns = [
    path("webhook/", stripe_seller_webhook, name="stripe_seller_webhook"),
    path("stripe/connect/", stripe_connect_page, name="stripe_connect_page"),
]
