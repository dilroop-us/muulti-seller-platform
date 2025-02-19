# coupons/utils
from django.core.exceptions import ObjectDoesNotExist
from coupons.models import Coupon, CustomerCoupon

def apply_coupon(customer, coupon_code, total_price):
    """
    Apply a coupon to the order and return updated price, discount amount, and coupon object.
    """
    try:
        coupon = Coupon.objects.get(code=coupon_code)
    except ObjectDoesNotExist:
        return {"success": False, "message": "Invalid coupon code.", "discount": 0, "new_total": total_price, "coupon": None}

    if not coupon.is_valid():
        return {"success": False, "message": "This coupon is expired or has been fully used.", "discount": 0, "new_total": total_price, "coupon": None}

    if CustomerCoupon.objects.filter(customer=customer, coupon=coupon).exists():
        return {"success": False, "message": "You have already used this coupon.", "discount": 0, "new_total": total_price, "coupon": None}

    discount = coupon.apply_discount(total_price)
    new_total = max(total_price - discount, 0)

    return {
        "success": True,
        "message": f"Coupon '{coupon_code}' applied successfully! You saved ${discount:.2f}.",
        "discount": discount,
        "new_total": new_total,
        "coupon": coupon
    }


def remove_coupon(request):
    """Remove applied coupon from session."""
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
        request.session.modified = True
