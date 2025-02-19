from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:product_id>/', views.add_review, name='add_review'),
    path('seller/', views.seller_reviews, name='seller_reviews'),
    path('admin/', views.admin_reviews, name='admin_reviews'),
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
]
