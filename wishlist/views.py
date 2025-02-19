from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Wishlist
from products.models import Product
from customer.models import CustomerProfile
from django.http import HttpResponse, JsonResponse
from django.contrib import messages


@login_required
def view_wishlist(request):
    """Render the wishlist page"""
    customer_profile = get_object_or_404(CustomerProfile, customer=request.user)
    wishlist, created = Wishlist.objects.get_or_create(customer_profile=customer_profile)

    return render(request, "wishlist/wishlist.html", {"wishlist": wishlist})

@login_required
def add_to_wishlist(request, product_id):
    """Add a product to the wishlist and redirect back"""

    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to add items to your wishlist.")
        return redirect("account_login")  # Redirect to login page

    customer_profile = get_object_or_404(CustomerProfile, customer=request.user)
    wishlist, created = Wishlist.objects.get_or_create(customer_profile=customer_profile)
    product = get_object_or_404(Product, id=product_id)

    wishlist.products.add(product)
    wishlist.save_to_cache()  # Update Redis cache

    messages.success(request, "Product added to your wishlist successfully.")
    return redirect("wishlist:wishlist")


@login_required
def remove_from_wishlist(request, product_id):
    """Remove a product from the wishlist and redirect back"""
    customer_profile = get_object_or_404(CustomerProfile, customer=request.user)
    wishlist = get_object_or_404(Wishlist, customer_profile=customer_profile)
    product = get_object_or_404(Product, id=product_id)

    wishlist.products.remove(product)
    wishlist.save_to_cache()  # Update Redis cache

    return redirect("wishlist:wishlist")

@login_required
def clear_wishlist(request):
    """Clear the wishlist and redirect back"""
    customer_profile = get_object_or_404(CustomerProfile, customer=request.user)
    wishlist = get_object_or_404(Wishlist, customer_profile=customer_profile)

    wishlist.products.clear()
    wishlist.save_to_cache()  # Update Redis cache

    return redirect("wishlist:wishlist")



def toggle_wishlist(request, product_id):
    """Toggle a product in the wishlist with HTMX support"""

    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to manage your wishlist.")
        return JsonResponse({"error": "Unauthorized"}, status=401)  # Unauthorized response for HTMX

    if request.method != "POST":
        return HttpResponse(status=405)

    customer_profile = get_object_or_404(CustomerProfile, customer=request.user)
    wishlist, created = Wishlist.objects.get_or_create(customer_profile=customer_profile)
    product = get_object_or_404(Product, id=product_id)

    if product in wishlist.products.all():
        wishlist.products.remove(product)
        wishlist.save_to_cache()
        return HttpResponse(f'<span id="wishlist-icon-{product.id}" hx-swap-oob="true">🤍</span>')
    else:
        wishlist.products.add(product)
        wishlist.save_to_cache()
        return HttpResponse(f'<span id="wishlist-icon-{product.id}" hx-swap-oob="true">❤️</span>')
