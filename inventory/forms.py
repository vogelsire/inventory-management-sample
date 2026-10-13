from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "description",
            "price",
            "stock",
            "is_active",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }