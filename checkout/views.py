# checkout/ views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.models import Cart, CartItem
from products.models import Product
from .models import Checkout, ShippingAddress
from customer.models import Customer
from .forms import ShippingAddressForm
from django.db import transaction
from django.core.cache import cache
from decimal import Decimal
import time
from payment.models import Payment, PaymentStatus
from orders.models import Order, OrderItem, StoreOrder, OrderStatus
from django.db.models import F
from coupons.utils import apply_coupon
from orders.tasks import send_order_confirmation_email



@login_required
def checkout_view(request):
    """Handles checkout logic and redirects based on payment method."""

    customer = get_object_or_404(Customer, id=request.user.id)
    cart = get_object_or_404(Cart, customer=customer)
    cart_items = CartItem.objects.filter(cart=cart)
    print(f"[INFO] Checkout request received from Customer: {customer.id}")


    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:cart")

    total_price = sum(item.get_total_price() for item in cart_items)
    shipping_addresses = customer.shipping_addresses.all()

    if request.method == "POST":
        shipping_address_id = request.POST.get("shipping_address")
        payment_method = request.POST.get("payment_method")

        if not shipping_address_id:
            messages.error(request, "Please select a shipping address.")
            return redirect("checkout:checkout_view")

        shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id, customer=customer)

        # ✅ Create or update checkout
        checkout, created = Checkout.objects.get_or_create(
            customer=customer,
            cart=cart,
            defaults={
                "shipping_address": shipping_address,
                "total_price": total_price,
                "payment_method": payment_method
            }
        )

        # ✅ Update checkout details
        checkout.shipping_address = shipping_address
        checkout.total_price = total_price
        checkout.payment_method = payment_method
        checkout.save()

        # ✅ Store checkout ID in Redis instead of session (Set expiration to 15 mins)
        cache.set(f"checkout:{customer.id}", checkout.id, timeout=900)

        if payment_method == "stripe":
            return redirect("payment:stripe_payment")

        elif payment_method == "cod":
            with transaction.atomic():

                payment = Payment.objects.create(
                    customer=checkout.customer,
                    checkout=checkout,
                    payment_method="cod",
                    amount=checkout.total_price,
                    status=PaymentStatus.PENDING
                )

                order = Order.objects.create(
                    customer=checkout.customer,
                    payment=payment,
                    shipping_address=checkout.shipping_address,
                    total_price=checkout.total_price,
                    payment_method="cod",
                )


                store_orders = {}
                for cart_item in CartItem.objects.filter(cart=cart):
                    product = cart_item.product
                    store = product.store

                    # ✅ Debug stock before updating
                    stock_before = Product.objects.filter(pk=product.pk).values("stock").first()
                    print(f"[DEBUG] {product.name} - Stock before update: {stock_before}")

                    if product.stock < cart_item.quantity:
                        print(f"[ERROR] Insufficient stock for {product.name} (Only {product.stock} left)")
                        raise ValueError(f"Insufficient stock for {product.name} (Only {product.stock} left)")

                    # ✅ Reduce stock
                    with transaction.atomic():
                        product = Product.objects.select_for_update().get(pk=cart_item.product.pk)

                        if product.stock < cart_item.quantity:
                            raise ValueError(f"Insufficient stock for {product.name}")

                        product.stock -= cart_item.quantity
                        product.save(update_fields=["stock"])


                    # ✅ Debug stock after updating
                    stock_after = Product.objects.filter(pk=product.pk).values("stock").first()
                    print(f"[DEBUG] {product.name} - Stock after update: {stock_after}")

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        store=store,
                        quantity=cart_item.quantity,
                        price=cart_item.get_total_price(),
                        status="pending"
                    )

                    print(f"[INFO] OrderItem Created for {product.name} - Quantity: {cart_item.quantity}")

                    if store not in store_orders:
                        store_orders[store] = StoreOrder.objects.create(
                            order=order,
                            store=store,
                            status="pending"
                        )

                send_order_confirmation_email.delay(order.id)

                CartItem.objects.filter(cart=cart).delete()
                checkout.delete()
                cache.delete(f"checkout:{customer.id}")

            messages.success(request, "Your order is being processed! Pay on delivery.")
            print(f"[SUCCESS] Order processed successfully for Customer: {customer.id}")
            return redirect("orders:order_summary", order_uuid=order.order_uuid)

    return render(request, "checkout/checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price,
        "shipping_addresses": shipping_addresses
    })



@login_required
def customer_addresses(request):
    """Display a list of customer addresses"""
    addresses = ShippingAddress.objects.filter(customer=request.user)
    return render(request, 'customer/list_addresses.html', {'addresses': addresses})


@login_required
def add_customer_address(request):
    """Add a new shipping address"""
    if request.method == "POST":
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.customer = request.user  # Assign the logged-in user
            address.save()
            messages.success(request, "Address added successfully!")
            return redirect('checkout:customer_addresses')  # Redirect to address list
    else:
        form = ShippingAddressForm()

    return render(request, 'checkout/add_address.html', {'form': form})


@login_required
def delete_address(request, address_id):
    """Delete a shipping address"""
    address = get_object_or_404(ShippingAddress, id=address_id, customer=request.user)

    if request.method == "POST":
        address.delete()
        messages.success(request, "Address deleted successfully!")
        return redirect('checkout:customer_addresses')  # Redirect to address list

    return render(request, 'customer/confirm_delete.html', {'address': address})
