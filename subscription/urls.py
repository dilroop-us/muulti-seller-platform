from django.urls import path
from .views import (
    payment_intro,
    create_checkout_session,
    stripe_subscription_webhook,
    payment_success,
    payment_failed,
)

app_name = "subscription"

urlpatterns = [
    path("intro/", payment_intro, name="intro"),
    path("checkout/", create_checkout_session, name="checkout-session"),
    path("webhook/", stripe_subscription_webhook, name="stripe-webhook"),
    path("payment-success/", payment_success, name="payment-success"),
    path("payment-failed/", payment_failed, name="payment-failed"),
]
