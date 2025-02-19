# coupons/forms
from django import forms
from .models import Coupon

class CouponApplyForm(forms.Form):
    """Form for entering a coupon code."""
    code = forms.CharField(label="Coupon Code", max_length=20)


class CouponForm(forms.ModelForm):
    """Form to create and update a coupon with better UX."""

    class Meta:
        model = Coupon
        fields = ['code', 'discount_type', 'value', 'valid_from', 'valid_to', 'usage_limit']
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'valid_to': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter coupon code'}),
            'discount_type': forms.Select(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'usage_limit': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def clean(self):
        """Ensure valid date range and logic."""
        cleaned_data = super().clean()
        valid_from = cleaned_data.get('valid_from')
        valid_to = cleaned_data.get('valid_to')

        if valid_from and valid_to and valid_from >= valid_to:
            raise forms.ValidationError("The 'valid from' date must be before the 'valid to' date.")

        return cleaned_data
