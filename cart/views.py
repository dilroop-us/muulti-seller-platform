# Cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from products.models import Product
from .models import CartItem
from .utils import get_or_create_cart, add_to_cart, update_cart_quantity, remove_from_cart


def cart(request):
    """Display the user's cart."""
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=cart).select_related("product")

    return render(request, "core/cart.html", {
        "cart_items": cart_items,
        "total_price": cart.get_subtotal(),
        "subtotal": cart.get_subtotal()
    })


def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = add_to_cart(request, product)

    # If the request is via htmx, return a fragment.
    if request.headers.get("HX-Request"):
        context = {
            "cart": cart,
            "product": product,
        }
        html = render_to_string("cart/mini_cart.html", context, request=request)
        return HttpResponse(html)

    # Fallback for non-htmx requests (if needed)
    return redirect("cart:cart")



def update_cart_view(request, product_id, action):
    cart = update_cart_quantity(request, product_id, action)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

    if request.headers.get("HX-Request"):
        # Render only the updated cart item row fragment.
        context = {"item": cart_item}
        html = render_to_string("cart/cart_item.html", context, request=request)
        return HttpResponse(html)
    else:
        return redirect("cart:cart")


def remove_from_cart_view(request, product_id):
    cart = remove_from_cart(request, product_id)
    if request.headers.get("HX-Request"):
        # You can return an empty response or a fragment to remove the element.
        return HttpResponse("")  # htmx can remove the element from the DOM
    return redirect("cart:cart")


def cart_total_view(request):
    cart = get_or_create_cart(request)
    total = float(cart.get_subtotal())
    return JsonResponse({"total_price": total})

