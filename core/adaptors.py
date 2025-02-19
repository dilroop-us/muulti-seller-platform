from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        """
        Handles redirection after login for authenticated users.
        """
        user = request.user
        if user.is_authenticated:
            if user.is_superuser:
                return resolve_url('custom_admin_dashboard')  # Use a named URL instead of a hardcoded path
            elif hasattr(user, 'is_seller') and user.is_seller:  # Ensure attribute exists
                return resolve_url('sellers:dashboard')
            elif hasattr(user, 'is_user') and user.is_user:
                return resolve_url('home')  # Assuming 'home' is the name of the home URL

        return super().get_login_redirect_url(request)

    def get_signup_redirect_url(self, request):
        """
        Handles redirection after signup for sellers and users.
        """
        user = request.user
        if user.is_authenticated:
            if hasattr(user, 'is_seller') and user.is_seller:
                return resolve_url('sellers:dashboard')
            elif hasattr(user, 'is_user') and user.is_user:
                return resolve_url('home')

        return super().get_signup_redirect_url(request)
