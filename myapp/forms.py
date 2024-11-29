from django import forms
from .models import Product, ProductVariation, Color, Size

# Form for Product
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'description']

    # keyword arguments
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['description'].required = False

# Form for Product Variation (multi-select for color and size)
class ProductVariationForm(forms.ModelForm):
    # Multi-select for colors and sizes
    color = forms.ModelMultipleChoiceField(queryset=Color.objects.all(), widget=forms.CheckboxSelectMultiple, required=True)
    size = forms.ModelMultipleChoiceField(queryset=Size.objects.all(), widget=forms.CheckboxSelectMultiple, required=True)

    class Meta:
        model = ProductVariation
        fields = ['product', 'image', 'quantity', 'price', 'color', 'size']
