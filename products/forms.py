from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """Form for sellers to create products under their store."""

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'discount', 'stock', 'categories']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Product Name'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Price'}),
            'discount': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'max': 100}),
            'stock': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        store = kwargs.pop('store', None)  # Get the store instance dynamically
        super().__init__(*args, **kwargs)
        if store:
            self.fields['categories'].queryset = Category.objects.all()


class CategoryForm(forms.ModelForm):
    """Form for admins to create categories."""

    class Meta:
        model = Category
        fields = ['name', 'parent']



class ProductUpdateForm(forms.ModelForm):
    is_available = forms.BooleanField(
        required=False,  # Ensure it's not required (unchecked = False)
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    class Meta:
        model = Product
        fields = ['is_available', 'stock', 'discount']
