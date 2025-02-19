import uuid
from django.core.exceptions import ValidationError
from .models import Cart
from django.db.models import Sum

def cart_item_count(request):
    """
    Make the total quantity of items in the cart available to every template.
    """
    total_quantity = 0

    # Ensure session is created
    if not request.session.session_key:
        request.session.create()  # Generate a session key if missing

    # Authenticated users
    if request.user.is_authenticated and hasattr(request.user, "customer"):
        cart = Cart.objects.filter(customer=request.user.customer).first()
        if cart:
            total_quantity = cart.cartitem_set.aggregate(total_qty=Sum("quantity"))["total_qty"] or 0

    else:
        # Guest users (session-based cart)
        session_id = request.session.session_key
        if session_id:
            try:
                # Convert session_id to UUID if needed
                session_uuid = uuid.UUID(session_id)
                cart = Cart.objects.filter(session_id=session_uuid).first()
            except (ValueError, ValidationError):
                cart = None  # Invalid UUID, ignore it

            if cart:
                total_quantity = cart.cartitem_set.aggregate(total_qty=Sum("quantity"))["total_qty"] or 0

    return {'cart_total_quantity': total_quantity}