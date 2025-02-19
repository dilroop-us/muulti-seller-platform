from django.http import HttpResponseForbidden
from functools import wraps

def customer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'user':
            return HttpResponseForbidden("You are not authorized.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
