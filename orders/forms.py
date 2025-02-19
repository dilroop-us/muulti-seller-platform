from django import forms
from .models import Order, OrderStatus, OrderItem, OrderItemStatus, StoreOrder, StoreOrderStatus

class AdminOrderStatusForm(forms.ModelForm):
    """Admin can update the order to any status."""
    status = forms.ChoiceField(
        choices=OrderStatus.choices,
        widget=forms.Select(attrs={"class": "w-full px-4 py-2 rounded border bg-gray-800 text-white"})
    )

    class Meta:
        model = Order
        fields = ["status"]


class SellerOrderItemStatusForm(forms.ModelForm):
    """Sellers can only update order item status (not the full order)."""
    status = forms.ChoiceField(
        choices=[
            (OrderItemStatus.PENDING, "Pending"),
            (OrderItemStatus.PROCESSING, "Processing"),
            (OrderItemStatus.SHIPPED, "Shipped"),
            (OrderItemStatus.DELIVERED, "Delivered"),
        ],
        widget=forms.Select(attrs={"class": "w-full px-4 py-2 rounded border bg-gray-800 text-white"})
    )

    class Meta:
        model = OrderItem
        fields = ["status"]


class SellerStoreOrderStatusForm(forms.ModelForm):
    """Sellers can update the overall store order status."""
    status = forms.ChoiceField(
        choices=[
            (OrderItemStatus.PENDING, "Pending"),
            (StoreOrderStatus.PROCESSING, "Processing"),
            (StoreOrderStatus.SHIPPED, "Shipped"),
            (StoreOrderStatus.COMPLETED, "Completed"),
        ],
        widget=forms.Select(attrs={"class": "w-full px-4 py-2 rounded border bg-gray-800 text-white"})
    )

    class Meta:
        model = StoreOrder
        fields = ["status"]
