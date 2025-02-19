from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product, Category
from django.core.paginator import Paginator
from reviews.models import Review
from django.db.models import Avg, Q, F, ExpressionWrapper, DecimalField
from customer.models import Customer
from django.contrib import messages
from .forms import ContactForm


def home(request):
    featured_products = Product.objects.filter(featured=True)  # Fetch only featured products
    reviews = Review.objects.all().select_related("customer")  # Fetch all reviews with customer details

    return render(request, "core/index.html", {
        'featured_products': featured_products,
        'reviews': reviews  # Pass reviews to template
    })


def about(request):
    return render(request, "core/about.html")



def shop(request):
    """Enhanced Shop View with Filters, Search, and Pagination based on Discounted Price."""
    query = request.GET.get("q", "")
    category_id = request.GET.get("category")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    # Annotate the discounted price to filter on it
    products = Product.objects.filter(is_available=True, stock__gt=0).annotate(
        discounted_price=ExpressionWrapper(
            F("price") - (F("price") * F("discount") / 100),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).order_by('-created_at')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if category_id:
        products = products.filter(categories__id=category_id)

    if min_price:
        products = products.filter(discounted_price__gte=min_price)

    if max_price:
        products = products.filter(discounted_price__lte=max_price)

    categories = Category.objects.filter(parent__isnull=True)

    # Pagination
    paginator = Paginator(products, 16)  # Show 16 products per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/shop.html", {
        "products": page_obj,
        "categories": categories,
        "query": query,
        "selected_category": category_id,
        "min_price": min_price,
        "max_price": max_price
    })



def shop_category(request, slug):
    """View to list products under a parent category and its subcategories."""

    # Fetch the selected parent category
    parent_category = get_object_or_404(Category, slug=slug)

    # Fetch all subcategories including the parent itself
    child_categories = parent_category.get_descendants(include_self=True)

    # Fetch products belonging to any of these categories
    products = Product.objects.filter(categories__in=child_categories).distinct()

    return render(request, 'core/shop.html', {
        'products': products,
        'category': parent_category
    })



def product_details(request, slug):
    """View to display product details with filtered reviews."""
    product = get_object_or_404(Product.objects.prefetch_related('categories'), slug=slug)

    # Filter reviews for the product
    latest_reviews = Review.objects.filter(product=product).order_by('-created_at')[:5]
    highest_rated_reviews = Review.objects.filter(product=product).order_by('-rating')[:5]
    lowest_rated_reviews = Review.objects.filter(product=product).order_by('rating')[:5]

    # Calculate the average rating
    average_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']

    context = {
        'product': product,
        'latest_reviews': latest_reviews,
        'highest_rated_reviews': highest_rated_reviews,
        'lowest_rated_reviews': lowest_rated_reviews,
        'average_rating': average_rating,
        'store': product.store,
    }

    return render(request, 'products/details.html', context)



def filter_reviews(request, product_id):
    """Filters reviews based on user selection."""
    product = get_object_or_404(Product, id=product_id)
    filter_type = request.GET.get("filter", "latest")

    if filter_type == "highest":
        reviews = Review.objects.filter(product=product).order_by('-rating')[:5]
    elif filter_type == "lowest":
        reviews = Review.objects.filter(product=product).order_by('rating')[:5]
    else:  # Default to latest reviews
        reviews = Review.objects.filter(product=product).order_by('-created_at')[:5]

    return render(request, "core/partials/reviews.html", {"reviews": reviews})





def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.send_email()  # Send email to admin
            messages.success(request, "Your message has been sent successfully!")
            return redirect("core:contact")  # Replace with your contact page URL name
    else:
        form = ContactForm()

    return render(request, "core/contact.html", {"form": form})



