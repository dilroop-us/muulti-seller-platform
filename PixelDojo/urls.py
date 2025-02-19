from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path('', include('core.urls', namespace='core')),
    path('customer/', include('customer.urls', namespace='customer')),
    path("seller/", include("seller.urls", namespace="seller")),
    path('products/', include('products.urls', namespace='product')),
    path('custom_admin/', include('custom_admin.urls', namespace='custom_admin')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('checkout/', include('checkout.urls', namespace='checkout')),
    path('payment/', include('payment.urls', namespace='payment')),
    path('wishlist/', include('wishlist.urls', namespace='wishlist')),
    path('seller_payments/', include('seller_payments.urls', namespace='seller_payments')),
    path('subscription/', include('subscription.urls', namespace='subscription')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('coupons/', include('coupons.urls', namespace='coupons')),
    path("__reload__/", include("django_browser_reload.urls")),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # ✅ Only add STATICFILES_DIRS if it exists
    if hasattr(settings, "STATICFILES_DIRS") and settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

