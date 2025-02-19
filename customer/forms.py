from django import forms
from django.core.exceptions import ValidationError
from django_countries.widgets import CountrySelectWidget
from .models import CustomerProfile
from allauth.account.forms import SignupForm


class CustomerSignupForm(SignupForm):
    """Custom Signup Form for Customers."""
    def save(self, request):
        user = super().save(request)
        user.role = "customer"  # ✅ Ensure role is set as customer
        user.save()
        return user


class EditProfileForm(forms.ModelForm):
    """Form for editing a user's profile."""
    class Meta:
        model = CustomerProfile
        fields = [
            'profile_image',
            'full_name',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'zip_code',
            'country',
            'date_of_birth',
            'phone',
        ]

        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date', 'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'full_name': forms.TextInput(
                attrs={'placeholder': 'Full Name', 'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'address_line_1': forms.TextInput(attrs={'placeholder': 'Street Address',
                                                     'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'address_line_2': forms.TextInput(attrs={'placeholder': 'Apartment, suite, unit, etc.',
                                                     'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'city': forms.TextInput(
                attrs={'placeholder': 'City', 'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'state': forms.TextInput(
                attrs={'placeholder': 'State', 'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'zip_code': forms.TextInput(
                attrs={'placeholder': 'Zip Code', 'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'country': CountrySelectWidget(attrs={'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
        }

    def clean_country(self):
        country = self.cleaned_data.get('country')
        if country not in ['US', 'CA']:  # Ensure the codes match the ones defined in `django-countries`
            raise ValidationError('Only United States and Canada are supported.')
        return country

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if not city:
            raise ValidationError('City is required.', code='invalid_city')
        return city



