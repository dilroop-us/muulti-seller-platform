# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('shop/', views.shop, name='shop'),
    path('contact/', views.contact, name='contact'),
    path('product/<slug:slug>/', views.product_details, name='product_details'),
    path('shop/category/<slug:slug>/', views.shop_category, name='shop_category'),
    path('filter/<int:product_id>/', views.filter_reviews, name='filter_reviews'),


]
