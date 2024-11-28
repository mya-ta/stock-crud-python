from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductVariation, Color, Size
from .forms import ProductForm, ProductVariationForm
from django.db.models import Prefetch
from django.http import HttpResponse

# View for Creating Product
def create_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST)

        if product_form.is_valid():
            # Save the product instance
            product = product_form.save()

            # Get the selected color and size choices from the form
            color_choices = request.POST.getlist('color')  # List of color IDs (not QuerySet)
            size_choices = request.POST.getlist('size')  # List of size IDs (not QuerySet)

            # Loop through all combinations of selected colors and sizes
            for color_id in color_choices:
                for size_id in size_choices:
                    try:
                        # Fetch individual Color and Size instances using get()
                        color = Color.objects.get(id=color_id)  # Single Color instance by ID
                    except Color.DoesNotExist:
                        color = None  # Handle the case where color does not exist

                    try:
                        size = Size.objects.get(id=size_id)  # Single Size instance by ID
                    except Size.DoesNotExist:
                        size = None  # Handle the case where size does not exist

                    # Ensure that both color and size are valid before creating the variation
                    if color and size:
                        # Create a new ProductVariation
                        variation = ProductVariation.objects.create(
                            product=product,
                            color=color,  # Assign the selected color (single instance)
                            size=size,    # Assign the selected size (single instance)
                            quantity=request.POST.get('quantity'),
                            price=request.POST.get('price'),
                        )
            return redirect('product_list')  # Redirect to the product list page after saving

    else:
        product_form = ProductForm()

    # Pass Color and Size choices to the template
    colors = Color.objects.all()
    sizes = Size.objects.all()

    return render(request, 'myapp/create_product.html', {'product_form': product_form, 'colors': colors, 'sizes': sizes})

# View for Listing Products and their Variations
def product_list(request):
    # Fetch product variations with related Product, Color, and Size objects
    product_variations = ProductVariation.objects.select_related(
        'product', 'color', 'size'
    )

    return render(request, 'myapp/product_list.html', {'product_variations': product_variations})
