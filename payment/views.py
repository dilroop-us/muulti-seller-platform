import stripe
import time
import json
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.cache import cache
from checkout.models import Checkout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from payment.models import Payment, PaymentStatus
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import transaction
from decimal import Decimal
from orders.models import Order, OrderItem, StoreOrder
from cart.models import Cart, CartItem
from seller.models import SellerStore
from django.db.models import F
from orders.tasks import send_order_confirmation_email


stripe.api_key = settings.STRIPE_SECRET_KEY



@login_required
def stripe_payment(request):
    """Handles Stripe payments."""
    checkout_id = cache.get(f"checkout:{request.user.id}")

    if not checkout_id:
        messages.error(request, "Checkout session expired. Please try again.")
        return redirect("checkout:checkout_view")

    checkout = get_object_or_404(Checkout, id=checkout_id)

    try:
        # ✅ Ensure a valid PaymentIntent is created with automatic charge creation
        intent = stripe.PaymentIntent.create(
            amount=int(checkout.total_price * 100),
            currency="usd",
            metadata={"checkout_id": str(checkout.id)},
            capture_method="automatic",  # ✅ Ensures charge is created immediately
            automatic_payment_methods={"enabled": True}  # ✅ Keep only this
        )

        print("✅ Payment Intent Created:", intent.client_secret)

        return render(request, "payment/stripe_payment.html", {
            "client_secret": intent.client_secret,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
            "checkout": checkout,
        })

    except stripe.error.StripeError as e:
        messages.error(request, f"Payment failed: {e.user_message if hasattr(e, 'user_message') else str(e)}")
        return redirect("checkout:checkout_view")



@login_required
def confirm_payment(request):
    """Confirms Stripe payment and creates order records without webhooks."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        payment_intent_id = data.get("payment_intent")

        if not payment_intent_id:
            return JsonResponse({"error": "Missing payment intent ID"}, status=400)

        # ✅ Retrieve Payment Intent
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError as e:
            return JsonResponse({"error": f"Stripe API error: {str(e)}"}, status=500)

        if intent.status != "succeeded":
            return JsonResponse({"error": f"Payment not completed. Status: {intent.status}"}, status=400)

        # ✅ Get Charge ID (Use latest_charge instead of charges.data)
        charge_id = intent.latest_charge  # ✅ Correct way to get charge ID
        if not charge_id:
            return JsonResponse({"error": "Charge ID not found. Payment may not have been processed yet."}, status=400)

        # ✅ Retrieve checkout ID from Redis
        checkout_id = cache.get(f"checkout:{request.user.id}")

        if not checkout_id:
            return JsonResponse({"error": "Checkout session expired. Please restart checkout."}, status=400)

        checkout = get_object_or_404(Checkout, id=checkout_id)
        cart = get_object_or_404(Cart, id=checkout.cart.id)

        with transaction.atomic():
            # ✅ 1. Create Payment Record with Charge ID
            payment = Payment.objects.create(
                customer=checkout.customer,
                checkout=checkout,
                payment_method="stripe",
                transaction_id=payment_intent_id,
                charge_id=charge_id,  # ✅ Now storing the correct Charge ID
                amount=Decimal(intent.amount) / 100,
                status=PaymentStatus.COMPLETED
            )

            # ✅ 2. Create Order
            order = Order.objects.create(
                customer=checkout.customer,
                payment=payment,
                shipping_address=checkout.shipping_address,
                total_price=checkout.total_price,
                payment_method="stripe",
            )

            # ✅ 3. Create Order Items & Store Orders
            store_orders = {}
            for cart_item in CartItem.objects.filter(cart=cart):
                product = cart_item.product
                store = product.store

                if product.stock < cart_item.quantity:
                    raise ValueError(f"Insufficient stock for {product.name} (Only {product.stock} left)")

                # ✅ Reduce stock
                with transaction.atomic():
                    product = Product.objects.select_for_update().get(pk=cart_item.product.pk)

                    if product.stock < cart_item.quantity:
                        raise ValueError(f"Insufficient stock for {product.name}")

                    product.stock -= cart_item.quantity
                    product.save(update_fields=["stock"])

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    store=store,
                    quantity=cart_item.quantity,
                    price=cart_item.get_total_price(),
                    status="pending"
                )

                if store not in store_orders:
                    store_orders[store] = StoreOrder.objects.create(
                        order=order,
                        store=store,
                        status="pending"
                    )

            send_order_confirmation_email.delay(order.id)

            # ✅ 4. Clear Cart & Checkout
            CartItem.objects.filter(cart=cart).delete()
            checkout.delete()
            cache.delete(f"checkout:{request.user.id}")

        return JsonResponse({"success": True, "order_uuid": str(order.order_uuid)})

    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)



@login_required
def payment_processing(request):
    """Temporary processing page while payment is confirmed."""
    return render(request, "payment/payment_processing.html")



@login_required
def verify_payment_status(request, payment_intent_id):
    """Manually checks payment status from Stripe API."""
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if intent.status == "succeeded":
            return JsonResponse({"status": "success"})
        elif intent.status == "requires_payment_method":
            return JsonResponse({"status": "failed"})
        else:
            return JsonResponse({"status": intent.status})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



@login_required
def order_complete(request, order_uuid):
    """Displays the order summary after successful payment."""
    order = get_object_or_404(Order, order_uuid=order_uuid)

    return render(request, "payment/order_complete.html", {"order": order})
