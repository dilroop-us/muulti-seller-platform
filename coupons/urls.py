from django.urls import path
from .views import coupon_list, coupon_create, coupon_edit, coupon_delete

app_name = 'coupons'

urlpatterns = [
    path('', coupon_list, name="admin_coupon_list"),
    path('create/', coupon_create, name="admin_coupon_create"),
    path('edit/<int:coupon_id>/', coupon_edit, name="admin_coupon_edit"),
    path('delete/<int:coupon_id>/', coupon_delete, name="admin_coupon_delete"),


]
