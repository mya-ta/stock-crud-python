import csv
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductVariation, Color, Size
from .forms import ProductForm, ProductVariationForm
from django.db.models import Prefetch
from django.http import HttpResponse

# To implement the functionality of exporting the filtered product variations from the search results 
# into a CSV file, use Python's built-in csv module to generate a CSV file based on the 
# ProductVariation table values displayed in the search results.

# View for Creating Product
def create_product(request):
    """
    View to create a new product, display variations, and search for variations.
    """
    if request.method == 'POST':
        if 'save' in request.POST:  # Save button clicked
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                # Save the product instance
                product = product_form.save()

                # Process product variations (colors and sizes)
                color_choices = request.POST.getlist('color')
                size_choices = request.POST.getlist('size')

                for color_id in color_choices:
                    for size_id in size_choices:
                        try:
                            color = Color.objects.get(id=color_id)
                            size = Size.objects.get(id=size_id)
                        except (Color.DoesNotExist, Size.DoesNotExist):
                            continue

                        # Create ProductVariation instances
                        ProductVariation.objects.create(
                            product=product,
                            color=color,
                            size=size,
                            quantity=request.POST.get('quantity'),
                            price=request.POST.get('price'),
                            image=request.FILES.get('image'),
                        )

                return redirect('product_list')  # Redirect after saving

        elif 'list' in request.POST:  # List button clicked
            return redirect('product_list')  # Show all products with variations

        elif 'generate' in request.POST:  # Search functionality clicked
            return search_product_variations(request)  # Call search function

        elif 'export_csv' in request.POST:  # Export CSV clicked
            return export_csv(request)  # Export the filtered variations to CSV

    else:
        product_form = ProductForm()

    # Render the form for creating a product
    return render(request, 'myapp/create_product.html', {
        'product_form': product_form,
        'colors': Color.objects.all(),
        'sizes': Size.objects.all(),
    })

# View for Listing Products and their Variations
def product_list(request):
    # Fetch product variations with related Product, Color, and Size objects
    product_variations = ProductVariation.objects.select_related(
        'product', 'color', 'size'
    )

    return render(request, 'myapp/product_list.html', {'product_variations': product_variations})

def update_product(request, id):
    # Fetch the existing product using the provided id
    product = get_object_or_404(ProductVariation, id=id)

    # Fetch the variations for this product (if any)
    product_variations = product.variations.all()

    if request.method == 'POST':
        # Initialize the ProductForm with the existing product data
        product_form = ProductForm(request.POST, instance=product)

        # Initialize ProductVariationForm with the existing variations (if any)
        variation_form = ProductVariationForm(request.POST)

        if product_form.is_valid():
            # Save the product instance
            product_form.save()

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

                    # Ensure that both color and size are valid before creating/updating the variation
                    if color and size:
                        # Check if a variation with this product, color, and size already exists
                        variation, created = ProductVariation.objects.get_or_create(
                            product=product,
                            color=color,
                            size=size,
                        )

                        # Update the variation fields if the variation exists
                        variation.quantity = request.POST.get('quantity')
                        variation.price = request.POST.get('price')
                        variation.image = request.FILES.get('image', variation.image)  # Keep the current image if no new one is uploaded
                        variation.save()

            # After successfully saving, redirect to product list
            return redirect('product_list')

    else:
        # If the request is GET, initialize the forms with the existing data
        product_form = ProductForm(instance=product)
        variation_form = ProductVariationForm()

    # Pass Color and Size choices to the template
    colors = Color.objects.all()
    sizes = Size.objects.all()

    return render(request, 'myapp/update_product.html', {
        'product_form': product_form,
        'variation_form': variation_form,
        'colors': colors,
        'sizes': sizes,
        'product': product,
        'product_variations': product_variations,
    })

def delete_product(request, id):
    # Get the ProductVariation object by ID
    variation = get_object_or_404(ProductVariation, id=id)
    
    # Delete the ProductVariation
    variation.delete()
    
    # Redirect to the product list page
    return redirect('product_list')

def search_product_variations(request):
    """
    Function to handle the search based on product name, color, and size.
    Filters the ProductVariations and returns the results.
    """
    search_name = request.POST.get('search_name', '')
    search_color = request.POST.get('search_color', '')
    search_size = request.POST.get('search_size', '')

    # Filter the ProductVariation model based on the search criteria
    variations = ProductVariation.objects.all()

    if search_name:
        variations = variations.filter(product__name__icontains=search_name)
    if search_color:
        variations = variations.filter(color__name__icontains=search_color)
    if search_size:
        variations = variations.filter(size__name__icontains=search_size)

    # Render the results of the search
    return render(request, 'myapp/create_product.html', {
        'variations': variations,
        'search_name': search_name,
        'search_color': search_color,
        'search_size': search_size,
        'colors': Color.objects.all(),
        'sizes': Size.objects.all(),
        'product_form': ProductForm(),  # Re-initialize product form for the page
    })

def export_csv(request):
    """
    Exports the search results of ProductVariation as a CSV file.
    """
    search_name = request.POST.get('search_name', '')
    search_color = request.POST.get('search_color', '')
    search_size = request.POST.get('search_size', '')

    # Filter the ProductVariation model based on the search criteria
    variations = ProductVariation.objects.all()

    if search_name:
        variations = variations.filter(product__name__icontains=search_name)
    if search_color:
        variations = variations.filter(color__name__icontains=search_color)
    if search_size:
        variations = variations.filter(size__name__icontains=search_size)

    # Create the HTTP response with the CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="product_variations.csv"'

    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow(['Product Name', 'Color', 'Size', 'Quantity', 'Price'])
    
    # Write the data rows
    for variation in variations:
        writer.writerow([variation.product.name, variation.color.name, variation.size.name, variation.quantity, variation.price])

    return response


def generate_unique_names(product_name, sku, color, size):
    pass