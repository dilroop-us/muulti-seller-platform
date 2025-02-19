import stripe
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from seller.models import SellerProfile
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY
site_url = settings.SITE_URL

@csrf_exempt
def stripe_seller_webhook(request):
    """Handle Stripe webhook events for seller accounts."""
    payload = request.body
    sig_header = request.headers.get("Stripe-Signature")

    # ✅ Fetch the webhook secret from settings
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    # 🔹 Log the event type for debugging
    print(f"🔹 Stripe Webhook Event: {event['type']}")

    # ✅ Handle account updates
    if event["type"] == "account.updated":
        account = event["data"]["object"]

        # ✅ Query SellerProfile instead of Seller
        seller_profile = SellerProfile.objects.filter(stripe_account_id=account["id"]).first()

        if seller_profile:
            seller_profile.is_onboarded = account.get("charges_enabled", False)
            seller_profile.save()
            print(f"✅ Seller {seller_profile.seller.email} onboarding updated.")
        else:
            print(f"⚠️ No seller found with Stripe Account ID: {account['id']}")

    return JsonResponse({"status": "success"})


@login_required
def stripe_connect_page(request):
    """Render the seller onboarding page with account details or onboarding link."""
    try:
        seller_profile = request.user.seller_profile  # Correct model access
    except SellerProfile.DoesNotExist:
        return render(request, "seller_payments/error.html", {"message": "You are not registered as a seller."})

    # If seller is not onboarded, generate an onboarding link
    if not seller_profile.is_onboarded or not seller_profile.stripe_account_id:
        account = stripe.Account.create(
            type="express",
            country="US",
            email=request.user.email,
        )
        seller_profile.stripe_account_id = account.id
        seller_profile.save()

        account_link = stripe.AccountLink.create(
            account=seller_profile.stripe_account_id,
            refresh_url=request.build_absolute_uri(f"{site_url}/seller_payments/stripe/connect/"),
            return_url=request.build_absolute_uri(f"{site_url}/seller/dashboard/"),
            type="account_onboarding",
        )
        return render(request, "seller_payments/stripe_connect.html", {
            "stripe_url": account_link.url,
            "is_onboarded": False,
        })

    # Fetch account details if onboarded
    stripe_account = stripe.Account.retrieve(seller_profile.stripe_account_id)

    # Retrieve payout details
    payouts = stripe.Payout.list(
        limit=5,
        stripe_account=seller_profile.stripe_account_id
    )

    # Convert payouts to a list
    payouts_list = list(payouts.auto_paging_iter())

    # Sort by created timestamp (just in case Stripe API response is unordered)
    payouts_list.sort(key=lambda x: x.created, reverse=True)

    return render(request, "seller_payments/stripe_connect.html", {
        "is_onboarded": seller_profile.is_onboarded,
        "stripe_account": stripe_account,
        "payouts": payouts_list,
    })

