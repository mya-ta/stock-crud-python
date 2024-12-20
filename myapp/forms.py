from django import forms
from .models import Product, ProductVariation, Color, Size

# Form for Product
class ProductForm(forms.ModelForm):
    colors = forms.ModelMultipleChoiceField(queryset=Color.objects.all(),widget=forms.CheckboxSelectMultiple,required=False)
    sizes = forms.ModelMultipleChoiceField(queryset=Size.objects.all(),widget=forms.CheckboxSelectMultiple,required=False)

    class Meta:
        model = Product
        fields = ['name', 'sku', 'description', 'colors', 'sizes']
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control custom-textarea', 'style': 'height: 100px'}))
    # keyword arguments
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['description'].label = 'Description:'
        self.fields['name'].label = 'Product Name:'
        self.fields['sku'].label = 'SKU:'

# Form for Product Variation (multi-select for color and size)
class ProductVariationForm(forms.ModelForm):
    # Multi-select for colors and sizes

    class Meta:
        model = ProductVariation
        fields = ['image', 'quantity', 'price']

    # Add additional fields if needed for updating Product attributes like name and SKU
    product_name = forms.CharField(max_length=255, required=False, label='Product Name')
    product_sku = forms.CharField(max_length=255, required=False, label='Product SKU')
    image = forms.ImageField(required=False, label='Product Image: ')
    quantity = forms.IntegerField(required=False, label='Quantity: ')
    price = forms.IntegerField(required=False, label='Price: ')

class ProductVari_UpdateForm(forms.Form):
    # class Meta:
    #     model = ProductVariation
    #     fields = ['product', 'image', 'quantity', 'price']

    image = forms.ImageField(required=False, label='Product Image:')
    quantity = forms.IntegerField(required=False, label='Quantity:')
    price = forms.IntegerField(required=False, label='Price:')
