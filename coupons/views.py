# coupons/views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Coupon
from .forms import CouponForm

# Custom decorator to check if the user is an admin
def admin_required(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(admin_required)
def coupon_list(request):
    """List all coupons"""
    coupons = Coupon.objects.all()
    return render(request, "coupon/coupon_list.html", {"coupons": coupons})


@user_passes_test(admin_required)
def coupon_create(request):
    """Create a new coupon"""
    if request.method == "POST":
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.created_by = request.user
            coupon.save()
            messages.success(request, "Coupon created successfully!")
            return redirect("coupons:admin_coupon_list")
    else:
        form = CouponForm()
    return render(request, "coupon/create_coupon.html", {"form": form})


@user_passes_test(admin_required)
def coupon_edit(request, coupon_id):
    """Edit an existing coupon"""
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == "POST":
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon updated successfully!")
            return redirect("coupons:admin_coupon_list")
    else:
        form = CouponForm(instance=coupon)
    return render(request, "coupon/create_coupon.html", {"form": form})


@user_passes_test(admin_required)
def coupon_delete(request, coupon_id):
    """Delete a coupon"""
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == "POST":
        coupon.delete()
        messages.success(request, "Coupon deleted successfully!")
        return redirect("coupons:admin_coupon_list")
    return render(request, "coupon/delete_coupon.html", {"coupon": coupon})
