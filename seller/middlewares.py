from django.shortcuts import redirect

class RestrictSellerAccessMiddleware:
    """Prevent customers from accessing seller login pages"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/seller/') and request.user.is_authenticated and not request.user.is_seller():
            return redirect('/')
        return self.get_response(request)
