import json
import stripe
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_POST
from seller.models import SellerProfile
from .models import Subscription

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def payment_intro(request):
    """
    Display the subscription plans with status check.
    """
    seller_profile = get_object_or_404(SellerProfile, seller=request.user)
    subscription = Subscription.objects.filter(seller_profile=seller_profile).first()

    return render(request, "subscription/plans.html", {
        "subscription": subscription,
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
    })



@login_required
def create_checkout_session(request):
    """
    Create a Stripe Checkout Session for a $100/year subscription.
    Redirects the seller to Stripe's hosted checkout page.
    """
    seller_profile = get_object_or_404(SellerProfile, seller=request.user)

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Seller Subscription",
                            "description": "Access to the seller platform for 1 year.",
                        },
                        "unit_amount": 10000,  # $100 in cents
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=settings.DOMAIN + "/subscription/payment-success/",
            cancel_url=settings.DOMAIN + "/subscription/payment-failed/",
            metadata={"seller_profile_id": str(seller_profile.id)},  # Attach seller ID
        )

        return redirect(checkout_session.url)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def stripe_subscription_webhook(request):
    """Handle Stripe webhooks to confirm payment success."""
    payload = request.body
    sig_header = request.headers.get("Stripe-Signature", "")


    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        seller_profile_id = session["metadata"].get("seller_profile_id")

        if not seller_profile_id:
            return JsonResponse({"error": "Missing metadata"}, status=400)

        try:
            subscription = Subscription.objects.get_or_create(seller_profile_id=seller_profile_id)[0]
            subscription.activate_subscription()
        except Subscription.DoesNotExist:
            return JsonResponse({"error": "Subscription not found"}, status=404)

    return JsonResponse({"status": "success"})


def payment_success(request):
    """Display a success message after a successful payment."""
    return render(request, "subscription/success.html")


def payment_failed(request):
    """Display a failure message if the payment fails."""
    return render(request, "subscription/failed.html")
