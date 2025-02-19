from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Product, SellerStore, Category
from .forms import ProductForm, CategoryForm, ProductUpdateForm
from django.db.models import Count, Avg
from orders.models import OrderItem, Order, OrderStatus
from reviews.models import Review
from .decorators import subscription_required

def is_admin(user):
    return user.is_superuser

def is_seller(user):
    return hasattr(user, 'store')  # Ensure the user has a store


@login_required
@user_passes_test(is_admin)
def create_category(request):
    """Only admin can create categories."""
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully!")
            return redirect('custom_admin:admin_category_list')
    else:
        form = CategoryForm()
    return render(request, "products/category_form.html", {"form": form})


@login_required
@user_passes_test(is_seller)
@subscription_required
def create_product(request):
    """Allow sellers to create products under their store."""
    store = request.user.store  # Get the seller's store

    if request.method == "POST":
        form = ProductForm(request.POST, store=store)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store  # Assign the seller's store
            product.save()
            form.save_m2m()  # Save many-to-many fields
            messages.success(request, "Product created successfully!")
            return redirect('products:seller_products')  # Redirect to product listing page
    else:
        form = ProductForm(store=store)

    return render(request, "products/product_form.html", {"form": form})

@login_required
@subscription_required
@user_passes_test(is_seller)
def seller_products_list(request):
    store = get_object_or_404(SellerStore, seller=request.user)
    products = Product.objects.filter(store=store)

    return render(request, 'products/product_list.html', {'products': products})


@login_required
@user_passes_test(is_seller)
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, store=request.user.store)
    old_values = {
        "is_available": product.is_available,
        "stock": product.stock,
        "discount": product.discount,
    }

    if request.method == "POST":
        form = ProductUpdateForm(request.POST, instance=product)

        if form.is_valid():
            product = form.save(commit=False)  # Get the instance but don't save yet

            # Handle checkbox being unchecked (set to False explicitly)
            product.is_available = "is_available" in request.POST  # This ensures False when unchecked

            # Detect what changed
            new_values = {
                "is_available": product.is_available,
                "stock": product.stock,
                "discount": product.discount,
            }

            # Print changes
            changes = {field: (old_values[field], new_values[field]) for field in old_values if
                       old_values[field] != new_values[field]}
            if changes:
                print(f"Product {product.id} updated with changes: {changes}")

            product.save()
            print(f"Saved Product {product.id} - is_available: {Product.objects.get(id=product.id).is_available}")
            messages.success(request, "Product updated successfully!")
            return redirect("product:product_detail", product_id=product.id)
        else:
            messages.error(request, "There was an error updating the product.")
    else:
        form = ProductUpdateForm(instance=product)

    return render(request, "products/update_product.html", {"form": form, "product": product})


@login_required
@user_passes_test(is_seller)
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Count sold items that are not canceled or refunded
    sold_count = OrderItem.objects.filter(
        product=product,
        order__status__in=[OrderStatus.PENDING, OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.DELIVERED]
    ).aggregate(total_sold=Count('id'))['total_sold'] or 0

    # Fetch reviews for this product
    reviews = Review.objects.filter(product=product)

    # Calculate the average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    context = {
        "product": product,
        "sold_count": sold_count,
        "reviews": reviews,
        "avg_rating": round(avg_rating, 1),
    }
    return render(request, "products/product_details.html", context)



@login_required
@user_passes_test(is_seller)
def delete_product(request, product_id):
    """Allow a seller to delete their own product."""
    product = get_object_or_404(Product, id=product_id, store=request.user.store)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect("products:seller_products")  # Redirect to the seller's product list

    return render(request, "products/product_confirm_delete.html", {"product": product})
