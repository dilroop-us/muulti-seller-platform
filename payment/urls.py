from django.urls import path
from .views import stripe_payment, confirm_payment, payment_processing, order_complete

app_name = "payment"

urlpatterns = [
    path("stripe/", stripe_payment, name="stripe_payment"),
    path("confirm-payment/", confirm_payment, name="confirm_payment"),

    path("processing/", payment_processing, name="payment_processing"),
    path("order-complete/<uuid:order_uuid>/", order_complete, name="order_complete"),

]
