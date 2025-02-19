from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from products.models import Product
from django.contrib.admin.views.decorators import staff_member_required


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = request.user
            review.product = product
            review.save()
            messages.success(request, "Review submitted successfully!")
            return redirect('core:product_details', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'reviews/add_review.html', {'form': form, 'product': product})


@login_required
def seller_reviews(request):
    reviews = Review.objects.filter(product__seller=request.user)  # Assuming seller field in Product model
    return render(request, 'reviews/seller_reviews.html', {'reviews': reviews})


@staff_member_required
def admin_reviews(request):
    reviews = Review.objects.all()
    return render(request, 'reviews/admin_reviews.html', {'reviews': reviews})


@staff_member_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    messages.success(request, "Review deleted successfully!")
    return redirect('admin_reviews')
