from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from seller.models import SellerProfile

def subscription_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You need to log in to access this page.")
            return redirect('seller:intro')

        if not request.user.is_seller():
            messages.error(request, "Only sellers can perform this action.")
            return redirect('seller:dashboard')

        try:
            seller_profile = request.user.seller_profile
        except SellerProfile.DoesNotExist:
            messages.error(request, "Seller profile not found.")
            return redirect('seller:dashboard')

        subscription = getattr(seller_profile, 'subscription', None)
        if not subscription or not subscription.is_active():
            messages.error(request, "Your subscription is inactive or expired. Please subscribe to continue.")
            return redirect('subscription:intro')

        # If all checks pass, proceed to the view
        return view_func(request, *args, **kwargs)

    return _wrapped_view
