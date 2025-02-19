from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from products.models import Category, Product
from products.forms import CategoryForm
from seller.models import Seller, SellerStore
from subscription.models import Subscription
from django.core.paginator import Paginator
from orders.models import Order, OrderStatus, OrderItem
from django.contrib import messages
import stripe
from django.conf import settings
from customer.models import CustomerProfile
from .stripe_utils import get_recent_payouts, get_charges_revenue, format_currency
from orders.forms import AdminOrderStatusForm
from django.db import transaction
from payment.models import PaymentStatus
from django.db.models import Count
from django.contrib.auth import logout
from django.core.cache import cache
from decimal import Decimal


stripe.api_key = settings.STRIPE_SECRET_KEY


@staff_member_required
def custom_admin_dashboard(request):

    return render(request, "admin/dashboard.html")


def custom_admin_logout(request):
    logout(request)
    return redirect('/')  # Redirect to home or login page


@staff_member_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, "admin/categories.html", {"categories": categories})

@staff_member_required
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("custom_admin:admin_category_list")
    else:
        form = CategoryForm()

    return render(request, "admin/add_category.html", {"form": form})


@staff_member_required
def seller_list(request):
    """View to list only sellers who have a store, with search, filtering, and pagination."""
    query = request.GET.get("q", "").strip()
    verified_filter = request.GET.get("verified", "")
    onboarded_filter = request.GET.get("onboarded", "")

    # Filter only sellers who have a store
    sellers = Seller.objects.filter(store__isnull=False).prefetch_related("store", "seller_profile__subscription")

    if query:
        sellers = sellers.filter(email__icontains=query)

    if verified_filter == "verified":
        sellers = sellers.filter(seller_profile__is_verified=True)
    elif verified_filter == "not_verified":
        sellers = sellers.filter(seller_profile__is_verified=False)

    if onboarded_filter == "yes":
        sellers = sellers.filter(seller_profile__is_onboarded=True)
    elif onboarded_filter == "no":
        sellers = sellers.filter(seller_profile__is_onboarded=False)

    sellers = sellers.order_by("id")

    # Pagination (10 sellers per page)
    paginator = Paginator(sellers, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "admin/seller_list.html", {
        "page_obj": page_obj,
        "query": query,
        "verified_filter": verified_filter,
        "onboarded_filter": onboarded_filter
    })



@staff_member_required
def customer_list(request):
    """View to list customer profiles with search, filtering, and pagination."""
    query = request.GET.get("q", "").strip()
    country_filter = request.GET.get("country", "")

    # Fetch only customer profiles
    customers = CustomerProfile.objects.select_related("customer").all()

    if query:
        customers = customers.filter(customer__email__icontains=query)

    if country_filter:
        customers = customers.filter(country=country_filter)

    customers = customers.order_by("-created_at")  # Most recent customers first

    # Pagination (10 customers per page)
    paginator = Paginator(customers, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "admin/customer_list.html", {
        "page_obj": page_obj,
        "query": query,
        "country_filter": country_filter
    })



@staff_member_required
def seller_detail(request, seller_id):
    """View to display a single seller's store and subscription details."""
    seller = get_object_or_404(Seller, id=seller_id)
    store = getattr(seller, "store", None)
    subscription = getattr(seller.seller_profile, "subscription", None)

    context = {
        "seller": seller,
        "store": store,
        "subscription": subscription,
    }
    return render(request, "admin/seller_detail.html", context)


@staff_member_required
def store_products(request, store_id):
    """View to list products specific to a store with pagination and search functionality."""

    store = get_object_or_404(SellerStore, id=store_id)
    query = request.GET.get("q", "").strip()

    # Fetch products related to the store (store instead of seller)
    products = Product.objects.filter(store=store).order_by("created_at")

    if query:
        products = products.filter(name__icontains=query)

    # Pagination (10 products per page)
    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "admin/store_products.html", {
        "store": store,
        "page_obj": page_obj,
        "query": query
    })


@staff_member_required
def order_list(request):
    """View to list all orders in the custom admin panel."""
    orders = Order.objects.select_related("customer", "payment").order_by("-created_at")

    # Pagination (10 orders per page)
    paginator = Paginator(orders, 10)
    page_number = request.GET.get("page")
    orders_page = paginator.get_page(page_number)

    context = {"orders": orders_page}
    return render(request, "admin/orders_list.html", context)


@staff_member_required
def order_detail(request, order_id):
    """View order details with related products, store, and status."""
    order = get_object_or_404(Order, id=order_id)

    # Fetch related order items including product and store details
    order_items = (
        OrderItem.objects
        .filter(order=order)
        .select_related("product", "product__store")  # Optimize queries
    )

    context = {
        "order": order,
        "order_items": order_items,
    }
    return render(request, "admin/order_detail.html", context)


@staff_member_required
def admin_update_order_status(request, order_id):
    """Admin can update the order status. If order is marked as 'Delivered', update payment to 'Completed'."""
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        form = AdminOrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            with transaction.atomic():  # ✅ Ensure atomic transaction
                order = form.save()

                # ✅ If order is marked as Delivered, update Payment Status
                if order.status == OrderStatus.DELIVERED and order.payment.status != PaymentStatus.COMPLETED:
                    order.payment.status = PaymentStatus.COMPLETED
                    order.payment.save(update_fields=["status"])

            return redirect("custom_admin:admin_orders")
    else:
        form = AdminOrderStatusForm(instance=order)

    return render(request, "admin/admin_order_status_update.html", {"form": form, "order": order})




@staff_member_required
def admin_store_products_view(request):
    # Automatically feature the top 10 best-selling products that are in stock
    top_selling_products = Product.objects.filter(is_available=True, stock__gt=0).order_by("-sold_count")[:10]

    # Reset all featured products first
    Product.objects.update(featured=False)

    # Set the top 10 selling products as featured
    Product.objects.filter(id__in=top_selling_products.values_list("id", flat=True)).update(featured=True)

    # Get the top 20 products for manual review
    display_products = Product.objects.filter(is_available=True, stock__gt=0).order_by("-sold_count")[:20]

    if request.method == "POST":
        # Allow admin to override automatic selection
        product_ids = request.POST.getlist("featured_products")  # Get selected product IDs
        Product.objects.update(featured=False)  # Reset all to False first
        Product.objects.filter(id__in=product_ids).update(featured=True)  # Set selected as featured
        messages.success(request, "Featured products updated successfully!")
        return redirect("custom_admin:admin_store_products")  # Redirect back

    return render(
        request, "admin/admin_products.html", {"products": display_products}
    )




@staff_member_required
def finance_dashboard(request):
    """Displays the Finance Dashboard with cached revenue and payouts."""

    cache_key = "finance_dashboard_data"
    cache_ttl = 3600  # Cache for 1 hour

    # Try to retrieve from cache
    context = cache.get(cache_key)

    if not context:
        try:
            # Fetch total revenue in cents and convert to dollars
            total_revenue_cents = get_charges_revenue(days=30)
            total_revenue_dollars = Decimal(total_revenue_cents) / 100  # Convert cents to USD

            # Fetch recent payouts (convert amounts if needed)
            payouts = get_recent_payouts(limit=10, days=30)
            for payout in payouts:
                payout["amount"] = Decimal(payout["amount"]) / 100  # Convert each payout from cents to USD

            context = {
                "total_revenue": f"{total_revenue_dollars:.2f}",  # Ensure 2 decimal places
                "payouts": payouts,
            }

            # Cache the result
            cache.set(cache_key, context, cache_ttl)

        except Exception as e:
            # Handle errors gracefully and log them
            context = {
                "total_revenue": "0.00",
                "payouts": [],
                "error": str(e),
            }

    return render(request, "admin/finance.html", context)


