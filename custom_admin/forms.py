from django import forms
from products.models import Category
from orders.models import Order, OrderStatus


class CategoryForm(forms.ModelForm):
    """Form to create categories with a parent-child relationship"""

    parent = forms.ModelChoiceField(
        queryset=Category.objects.filter(parent__isnull=True),  # Only main categories
        required=False,
        empty_label="(Main Category)",
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
    )

    class Meta:
        model = Category
        fields = ['name', 'parent']

    def clean_name(self):
        name = self.cleaned_data.get("name")
        parent = self.cleaned_data.get("parent")

        if Category.objects.filter(name=name, parent=parent).exists():
            raise forms.ValidationError("A category with this name already exists under this parent.")

        return name

