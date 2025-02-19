from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import EditProfileForm
from .models import CustomerProfile, Customer
from django.contrib import messages
from django.views.decorators.cache import never_cache
from orders.models import Order, OrderStatus, OrderItem
from django.http import HttpResponse
from django.db import transaction
from payment.models import Payment, PaymentStatus

@login_required
@never_cache
def profile_view(request):
    if not isinstance(request.user, Customer):
        try:
            user = Customer.objects.get(username=request.user.username)
        except Customer.DoesNotExist:
            messages.error(request, "User not found. Please log in again.")
            return render(request, "customer/profile.html", {"profile": None, "user": None})
    else:
        user = request.user

    # Fetch or create CustomerProfile
    profile, created = CustomerProfile.objects.get_or_create(customer=user)

    if created:
        messages.info(request, "Your profile has been created.")

    messages.success(request, f"Welcome {user.first_name}")

    # ✅ Explicitly pass user & profile to the template
    return render(request, "customer/profile.html", {"profile": profile, "user": user})



@login_required
@never_cache
def edit_profile(request):
    profile = get_object_or_404(CustomerProfile, customer=request.user)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('customer:profile')
        else:
            messages.error(request, 'There were errors in your form submission.')
    else:
        form = EditProfileForm(instance=profile)

    return render(request, 'customer/edit_profile.html', {'form': form})




@login_required
def payment_history(request):
    """View to display the payment history of the logged-in customer."""
    if not request.user.is_customer():  # Ensure only customers access this view
        return render(request, "403.html", status=403)

    payments = Payment.objects.filter(customer=request.user).order_by("-created_at")

    return render(request, "customer/payment_history.html", {"payments": payments})



