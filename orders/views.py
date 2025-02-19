from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, StoreOrder, OrderStatus, OrderItemStatus, StoreOrderStatus
from payment.models import Payment, PaymentStatus, PaymentMethod
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, F
from datetime import datetime
from .forms import SellerStoreOrderStatusForm, SellerOrderItemStatusForm
from seller.models import SellerStore
from django.core.cache import cache
from django.db import transaction
from products.models import Product
import stripe
from django.conf import settings
from orders.tasks import send_order_cancellation_email


stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def order_status_api(request):
    """Return the latest order for the logged-in user."""
    order = Order.objects.filter(customer=request.user).order_by("-created_at").first()
    if order:
        return JsonResponse({"order_uuid": str(order.order_uuid)})  # ✅ Return order_uuid
    return JsonResponse({"order_uuid": None})



@login_required
def order_summary(request, order_uuid):
    """Display order summary with order items."""
    order = get_object_or_404(Order, order_uuid=order_uuid)
    order_items = OrderItem.objects.filter(order=order)

    return render(
        request,
        "orders/order_summary.html",
        {"order": order, "items": order_items},
    )



@login_required
def order_list(request):
    """List all orders of a customer with filtering and pagination."""
    status = request.GET.get("status")
    payment_method = request.GET.get("payment_method")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    orders = Order.objects.filter(customer=request.user).order_by("-created_at")

    if status:
        orders = orders.filter(status=status)
    if payment_method:
        orders = orders.filter(payment_method=payment_method)
    if start_date:
        orders = orders.filter(created_at__date__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__date__lte=end_date)

    paginator = Paginator(orders, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "orders/order_list.html", {"page_obj": page_obj})



@login_required
def cancel_order(request, order_uuid):
    """Cancel an order, restore stock, and refund if paid via Stripe."""
    order = get_object_or_404(Order, order_uuid=order_uuid, customer=request.user)

    if order.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
        messages.error(request, "Only pending or processing orders can be canceled.")
        return redirect("orders:order_list")

    try:
        with transaction.atomic():
            # ✅ 1. Update Order Status to Canceled
            order.status = OrderStatus.CANCELED
            order.save(update_fields=["status"])

            # ✅ 2. Handle Payment Status (Refund if Stripe)
            payment = order.payment
            refund_success = False  # Default to False

            if order.payment_method == PaymentMethod.COD:
                # ✅ COD Orders: Just mark payment as canceled
                payment.status = PaymentStatus.CANCELED
                payment.save(update_fields=["status"])
                refund_success = True  # ✅ COD doesn't require refunds

            elif order.payment_method == PaymentMethod.STRIPE:
                charge_id = payment.charge_id

                if charge_id:
                    try:
                        # ✅ Check if the Charge is Already Refunded
                        charge = stripe.Charge.retrieve(charge_id)

                        if charge.refunded:  # ✅ Charge is already refunded
                            messages.info(request, "Payment has already been refunded.")
                            refund_success = True
                        else:
                            # ✅ Process the refund using Charge ID
                            refund = stripe.Refund.create(
                                charge=charge_id,
                                amount=int(order.total_price * 100)  # Convert to cents
                            )

                            if refund.status == "succeeded":
                                # ✅ Refresh payment object to ensure it reflects changes
                                payment.refresh_from_db()

                                payment.status = PaymentStatus.REFUNDED  # ✅ Update Payment Status
                                payment.save(update_fields=["status"])

                                order.status = OrderStatus.CANCELED  # ✅ Update Order Status
                                order.save(update_fields=["status"])


                                refund_success = True  # ✅ Refund was successful
                                messages.success(request, "Order canceled and payment refunded successfully.")
                            else:
                                messages.error(request, "Failed to refund payment via Stripe.")

                    except stripe.error.StripeError as e:
                        messages.error(request, f"Stripe refund error: {str(e)}")
                else:
                    messages.error(request, "No Stripe charge ID found. Refund failed.")

            # ✅ 3. Cancel Order Items & Restore Stock (Only if refund succeeded or COD)
            if refund_success:
                for item in order.items.all():
                    if item.status not in [OrderItemStatus.CANCELED, OrderItemStatus.REFUNDED]:  # Prevent double cancellations
                        item.status = OrderItemStatus.CANCELED
                        item.save(update_fields=["status"])

                        # ✅ Restore stock for canceled items
                        Product.objects.filter(pk=item.product.pk).update(
                            stock=F("stock") + item.quantity
                        )

            # ✅ 4. Update Store Order Statuses to Canceled
            for store_order in order.store_orders.all():
                store_order.status = StoreOrderStatus.CANCELED
                store_order.save(update_fields=["status"])

            send_order_cancellation_email.delay(order.id)

            return redirect("orders:order_list")

    except Exception as e:
        messages.error(request, f"An error occurred while canceling the order: {e}")
        return redirect("orders:order_list")



@login_required
def seller_update_store_order_status(request, store_order_id):
    """Allows a seller to update the status of a specific store order."""

    # Ensure the user has a store
    seller_store = SellerStore.objects.filter(seller=request.user).first()
    if not seller_store:
        return JsonResponse({"error": "You do not own a store."}, status=403)

    # Fetch the store order linked to the seller's store
    store_order = get_object_or_404(StoreOrder, id=store_order_id, store=seller_store)

    if request.method == "POST":
        form = SellerStoreOrderStatusForm(request.POST, instance=store_order)
        if form.is_valid():
            form.save()
            return redirect("seller:seller_orders")

    else:
        form = SellerStoreOrderStatusForm(instance=store_order)

    return render(request, "seller/store_order_update.html", {"form": form, "store_order": store_order})




@login_required
def seller_update_order_item_status(request, order_item_id):
    """Allows a seller to update the status of a specific order item."""

    # Ensure the user has a store
    seller_store = SellerStore.objects.filter(seller=request.user).first()
    if not seller_store:
        return JsonResponse({"error": "You do not own a store."}, status=403)

    # Fetch the correct order item using seller's store
    order_item = get_object_or_404(OrderItem, id=order_item_id, store=seller_store)

    if request.method == "POST":
        form = SellerOrderItemStatusForm(request.POST, instance=order_item)
        if form.is_valid():
            form.save()
            return redirect("seller:seller_orders")

    else:
        form = SellerOrderItemStatusForm(instance=order_item)

    return render(request, "seller/order_item_update.html", {"form": form, "order_item": order_item})


