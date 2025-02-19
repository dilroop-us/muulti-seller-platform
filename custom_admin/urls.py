from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    custom_admin_dashboard, category_list,
    add_category, seller_detail,
    seller_list, store_products,
    order_list, order_detail,
    admin_update_order_status, admin_store_products_view,
    finance_dashboard, customer_list, custom_admin_logout


)

app_name = 'custom_admin'

urlpatterns = [
    path('custom_admin', custom_admin_dashboard, name='dashboard'),
    path('categories/', category_list, name="admin_category_list"),
    path('customer_list/', customer_list, name="admin_customer_list"),
    path('categories/add/', add_category, name="admin_add_category"),
    path("admin/sellers/", seller_list, name="seller_list"),
    path("admin/sellers/<int:seller_id>/", seller_detail, name="seller_detail"),
    path("admin/stores/<int:store_id>/products/", store_products, name="store_products"),
    path("orders/", order_list, name="admin_orders"),
    path("orders/<int:order_id>/", order_detail, name="admin_order_detail"),
    path("orders/update-status/<int:order_id>/", admin_update_order_status, name="admin_update_order_status"),
    path('admin/store-products/', admin_store_products_view, name='admin_store_products'),
    path("finance-dashboard/", finance_dashboard, name="finance_dashboard"),
    path("logout/", custom_admin_logout, name="admin_logout"),

]


