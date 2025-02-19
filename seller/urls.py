from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import SellerPasswordResetForm
from .views import (
    seller_register_view, seller_login_view, seller_logout_view,
    seller_profile_view, edit_seller_profile_view, intro, dashboard,
    seller_store_orders_list, seller_store_order_detail_view
)

app_name = 'seller'

urlpatterns = [
    path('', intro, name='intro'),
    path('register/', seller_register_view, name='seller_register'),
    path('login/', seller_login_view, name='seller_login'),
    path('logout/', seller_logout_view, name='seller_logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', seller_profile_view, name='seller_profile'),
    path('profile/edit/', edit_seller_profile_view, name='edit_seller_profile'),
    path("orders/", seller_store_orders_list, name="seller_store_orders"),
    path("orders/store/<int:store_order_id>/", seller_store_order_detail_view, name="seller_store_order_detail"),

    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name="seller/password/password_reset.html",
        form_class=SellerPasswordResetForm,
        success_url='/seller/password_reset/done/',
        email_template_name="seller/password/password_reset_email.html",
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name="seller/password/password_reset_done.html",
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="seller/password/password_reset_confirm.html",
        success_url='/seller/reset/done/'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name="seller/password/password_reset_complete.html"
    ), name='password_reset_complete'),
]
