from django.urls import path
from .views import (
    order_summary,
    order_list,
    order_status_api,
    seller_update_store_order_status,
    seller_update_order_item_status,
    cancel_order
)

app_name = "orders"

urlpatterns = [
    path("summary/<uuid:order_uuid>/", order_summary, name="order_summary"),
    path("cancel/<uuid:order_uuid>/", cancel_order, name="cancel_order"),
    path("list/", order_list, name="order_list"),
    path("update-status/<int:order_item_id>/", seller_update_order_item_status, name="update_order_status"),
    path("store-update-status/<int:store_order_id>/", seller_update_store_order_status, name="store_update_status"),
    path("order-status/", order_status_api, name="order_status_api"),
]
