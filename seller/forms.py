from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth import authenticate
from .models import Seller, SellerProfile, SellerStore
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class SellerLoginForm(AuthenticationForm):
    """Custom authentication form for sellers using email instead of username."""

    def __init__(self, request=None, *args, **kwargs):
        """Store request to use in authentication."""
        self.request = request
        super().__init__(request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Email', 'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-control'})

    def clean(self):
        """Validate seller role and authenticate using email."""
        cleaned_data = super().clean()
        email = cleaned_data.get('username')  # ✅ Email is stored as `username`
        password = cleaned_data.get('password')

        if email and password:
            # ✅ Ensure `authenticate` is looking up the correct field
            user = authenticate(self.request, username=email, password=password)

            if user is not None:
                if user.is_superuser or user.role == 'admin':  # ✅ Allow superusers & admins
                    return cleaned_data
                elif user.role != 'seller':
                    raise forms.ValidationError("Only sellers can log in here.")
            else:
                raise forms.ValidationError("Invalid email or password.")

        return cleaned_data


class SellerRegistrationForm(UserCreationForm):
    """Form for seller registration with improved styling and placeholders"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full border-gray-300 p-2 rounded-lg', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full border-gray-300 p-2 rounded-lg', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'w-full border-gray-300 p-2 rounded-lg', 'placeholder': 'Email Address'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full border-gray-300 p-2 rounded-lg', 'placeholder': 'Password'}),
        label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full border-gray-300 p-2 rounded-lg', 'placeholder': 'Confirm Password'}),
        label="Confirm Password"
    )

    class Meta:
        model = Seller
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        """Save seller and create associated profile & store"""
        seller = super().save(commit=False)
        seller.role = "seller"

        # Ensure username is always set
        if not seller.username:
            seller.username = seller.email

        # Make sure password is hashed
        seller.set_password(self.cleaned_data["password1"])

        if commit:
            seller.save()
        return seller




class SellerProfileForm(forms.ModelForm):
    """Form for editing seller profile"""

    class Meta:
        model = SellerProfile
        fields = ['profile_image']


class SellerStoreForm(forms.ModelForm):
    """Form for editing seller store information"""

    class Meta:
        model = SellerStore
        fields = [
            'owner_name','store_name', 'store_logo', 'store_address_line_1', 'store_address_line_2',
            'store_city', 'store_state', 'store_country', 'store_zip_code',
             'phone_number', 'tax_id', 'bank_account_number'
        ]


class SellerPasswordResetForm(PasswordResetForm):
    """Custom password reset form for sellers"""
    def clean_email(self):
        email = self.cleaned_data['email']
        if not Seller.objects.filter(email=email).exists():
            raise forms.ValidationError("No account found with this email.")
        return email



