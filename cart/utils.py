#  cart/utils.py
from .models import Cart, CartItem
from django.shortcuts import get_object_or_404
from uuid import uuid4
from products.models import Product


def get_or_create_cart(request):
    """Retrieve or create a cart for a logged-in user or guest session."""
    if request.user.is_authenticated:
        guest_cart = Cart.objects.filter(session_id=request.session.get("session_id")).first()
        user_cart, created = Cart.objects.get_or_create(customer=request.user)

        # Merge guest cart into user cart
        if guest_cart and guest_cart != user_cart:
            for item in guest_cart.cartitem_set.all():
                cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=item.product)
                if not created:
                    cart_item.quantity += item.quantity
                    cart_item.save()
                item.delete()

            guest_cart.delete()
            del request.session["session_id"]

        return user_cart

    session_id = request.session.get("session_id", str(uuid4()))
    request.session["session_id"] = session_id
    cart, _ = Cart.objects.get_or_create(session_id=session_id, customer=None)
    return cart


def add_to_cart(request, product, quantity=1):
    """Add a product to the cart or update quantity if it exists."""
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return cart


def update_cart_quantity(request, product_id, action):
    """Increase or decrease cart item quantity safely within stock limits."""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    product = get_object_or_404(Product, id=product_id)  # Fetch the product to get stock info

    if action == "increase":
        if cart_item.quantity < product.stock:  # Ensure it does not exceed stock
            cart_item.quantity += 1
        else:
            return JsonResponse({"error": "Cannot increase beyond available stock"}, status=400)
    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1

    cart_item.save()
    return cart


def remove_from_cart(request, product_id):
    """Remove a product from the cart."""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()
    return cart
