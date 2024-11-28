from django import forms
from .models import Product, ProductVariation, Color, Size

# Form for Product
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description']

# Form for Product Variation (multi-select for color and size)
class ProductVariationForm(forms.ModelForm):
    # Multi-select for colors and sizes
    color = forms.ModelMultipleChoiceField(queryset=Color.objects.all(), widget=forms.CheckboxSelectMultiple, required=True)
    size = forms.ModelMultipleChoiceField(queryset=Size.objects.all(), widget=forms.CheckboxSelectMultiple, required=True)

    class Meta:
        model = ProductVariation
        fields = ['image', 'quantity', 'price', 'color', 'size']
