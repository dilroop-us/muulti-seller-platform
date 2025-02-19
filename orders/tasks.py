from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from orders.models import Order


@shared_task
def send_order_confirmation_email(order_id):
    """Sends an order confirmation email to the customer."""
    order = Order.objects.get(id=order_id)
    subject = "Order Confirmation - Your Order has been placed!"

    # ✅ Render email template with order details
    html_message = render_to_string("emails/order_confirmation.html", {"order": order})
    plain_message = strip_tags(html_message)  # Convert to plain text

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.customer.email],
        html_message=html_message
    )

    return f"Order confirmation email sent to {order.customer.email}"





@shared_task
def send_order_cancellation_email(order_id):
    """Sends an order cancellation email to the customer."""
    order = Order.objects.get(id=order_id)
    subject = "Order Cancellation - Your Order has been canceled"

    # ✅ Render email template with order details
    html_message = render_to_string("emails/order_cancellation.html", {"order": order})
    plain_message = strip_tags(html_message)  # Convert to plain text

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.customer.email],
        html_message=html_message
    )

    return f"Order cancellation email sent to {order.customer.email}"
