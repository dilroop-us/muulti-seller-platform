from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_backends
from .forms import SellerRegistrationForm, SellerProfileForm, SellerStoreForm, SellerLoginForm
from django.contrib.auth.decorators import login_required
from .models import SellerProfile, SellerStore
from django.contrib import messages
from .tasks import validate_id
import redis
from django.core.paginator import Paginator
from orders.models import  Order, OrderItem, StoreOrder
from django.http import JsonResponse
from orders.forms import SellerStoreOrderStatusForm, SellerOrderItemStatusForm


# Redis Connection
redis_client = redis.StrictRedis(host='localhost', port=6380, db=0, decode_responses=True)


def intro(request):
    return render(request, 'intro.html')

def seller_login_view(request):
    """Login view for sellers, with redirection for superusers and admins."""

    if request.user.is_authenticated:
        if request.user.is_superuser or (hasattr(request.user, "role") and request.user.role == "admin"):
            return redirect("custom_admin:dashboard")
        elif hasattr(request.user, "role") and request.user.role == "seller":
            return redirect("seller:dashboard")
        messages.error(request, "You are already logged in with a different role.")
        return redirect("core:home")

    if request.method == "POST":
        form = SellerLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                # Redirect based on role
                if user.is_superuser or user.role == "admin":
                    login(request, user)
                    return redirect("custom_admin:dashboard")
                elif user.role == "seller":
                    login(request, user)
                    return redirect("seller:dashboard")
                else:
                    messages.error(request, "Only sellers can log in here.")
        else:
            messages.error(request, "Invalid email or password.")
            print(f"❌ Debug: Form validation failed: {form.errors}")
    else:
        form = SellerLoginForm()

    return render(request, "seller/seller_login.html", {"form": form})


def seller_register_view(request):
    """View for seller registration"""
    if request.user.is_authenticated and request.user.is_seller():
        return redirect('/seller/dashboard/')

    if request.method == "POST":
        form = SellerRegistrationForm(request.POST)
        if form.is_valid():
            seller = form.save()

            backend = get_backends()[1]
            seller.backend = f"{backend.__module__}.{backend.__class__.__name__}"

            login(request, seller)  # Log in the user after registration
            return redirect('/seller/dashboard/')
    else:
        form = SellerRegistrationForm()

    return render(request, 'seller/seller_register.html', {'form': form})

@login_required
def seller_profile_view(request):
    """View for displaying seller profile and store details"""
    if not request.user.is_authenticated or not request.user.is_seller():
        return redirect('/seller/login/')

    seller = request.user
    profile = get_object_or_404(SellerProfile, seller=seller)
    store = get_object_or_404(SellerStore, seller=seller)

    return render(request, 'seller/seller_profile.html', {
        'profile': profile,
        'store': store
    })


@login_required
def dashboard(request):
    return render(request, 'seller/dashboard.html')



@login_required
def edit_seller_profile_view(request):
    """View for editing seller profile and store information, and verifying store tax ID"""

    if not request.user.is_seller():  # Ensure the user is a seller
        return redirect('/seller/login/')

    seller = request.user
    profile = SellerProfile.objects.get(seller=seller)
    store = SellerStore.objects.get(seller=seller)

    if request.method == "POST":
        profile_form = SellerProfileForm(request.POST, request.FILES, instance=profile)
        store_form = SellerStoreForm(request.POST, request.FILES, instance=store)

        if profile_form.is_valid() and store_form.is_valid():
            profile_form.save()
            store_form.save()


            if store.tax_id:
                task_result = validate_id.delay(store.tax_id)

                messages.info(request, "Profile updated. Store verification in progress.")
            else:
                messages.warning(request, "Profile updated, but no Tax ID provided for verification.")

            return redirect('seller:seller_profile')  # Redirect after successful update

    else:
        profile_form = SellerProfileForm(instance=profile)
        store_form = SellerStoreForm(instance=store)

    return render(request, 'seller/edit_profile.html', {
        'profile_form': profile_form,
        'store_form': store_form
    })


def seller_logout_view(request):
    logout(request)
    return redirect('/seller/login/')



@login_required
def seller_store_orders_list(request):
    """View to list all orders for the seller's store"""
    seller_store = get_object_or_404(SellerStore, seller=request.user)
    store_orders = StoreOrder.objects.filter(store=seller_store).select_related("order").order_by("-order__created_at")

    # Pagination (10 orders per page)
    paginator = Paginator(store_orders, 10)
    page_number = request.GET.get("page")
    orders_page = paginator.get_page(page_number)

    return render(request, "seller/orders_list.html", {"orders": orders_page})



@login_required
def seller_store_order_detail_view(request, store_order_id):
    """
    View for a seller to:
    - See details of their StoreOrder
    - Update the StoreOrder status
    - Update individual OrderItem statuses
    """
    seller_store = get_object_or_404(SellerStore, seller=request.user)
    store_order = get_object_or_404(StoreOrder, id=store_order_id, store=seller_store)
    order_items = OrderItem.objects.filter(order=store_order.order, store=seller_store)

    if request.method == "POST":
        if "store_status_update" in request.POST:  # Store order update form
            store_form = SellerStoreOrderStatusForm(request.POST, instance=store_order)
            if store_form.is_valid():
                store_form.save()
                store_order.order.update_order_status()  # Update overall order status
                messages.success(request, "Store order status updated successfully.")
                return redirect("seller:seller_store_order_detail", store_order_id=store_order.id)

        elif "order_item_update" in request.POST:  # Updating individual order items
            order_item_id = request.POST.get("order_item_id")
            order_item = get_object_or_404(OrderItem, id=order_item_id, store=seller_store)

            item_form = SellerOrderItemStatusForm(request.POST, instance=order_item)
            if item_form.is_valid():
                item_form.save()
                order_item.order.update_order_status()  # Update order status
                messages.success(request, "Order item status updated successfully.")
                return redirect("seller:seller_store_order_detail", store_order_id=store_order.id)

    else:
        store_form = SellerStoreOrderStatusForm(instance=store_order)
        item_forms = {item.id: SellerOrderItemStatusForm(instance=item).as_p() for item in order_items}

    return render(request, "seller/store_order_detail.html", {
        "store_order": store_order,
        "order_items": order_items,
        "order": store_order.order,
        "store_form": store_form,
        "item_forms": item_forms,
    })




def seller_password_reset_done(request):
    """Custom view for displaying a password reset confirmation message"""
    messages.success(request, "An email with password reset instructions has been sent if the email exists in our system.")
    return render(request, 'seller/password_reset_done.html')



@login_required
def seller_order_items(request):
    """View to list all individual order items from the seller's store."""

    seller_store = SellerStore.objects.filter(seller=request.user).first()

    if not seller_store:
        return render(request, "seller/order_items_list.html", {"order_items": None, "error": "No store found for this seller."})

    order_items = OrderItem.objects.filter(
        store=seller_store
    ).select_related("order", "product").order_by("-order__created_at")

    paginator = Paginator(order_items, 10)
    page_number = request.GET.get("page")
    order_items_page = paginator.get_page(page_number)

    context = {"order_items": order_items_page}
    return render(request, "seller/order_items_list.html", context)
