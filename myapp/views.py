import csv
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductVariation, Color, Size
from .forms import ProductForm, ProductVariationForm
from django.db.models import Prefetch
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

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
    # Fetch the ProductVariation instance by ID (which is passed as 'id')
    variation = get_object_or_404(ProductVariation, id=id)
   
    # Get the related Product instance from the ProductVariation
    product = variation.product

    print(f"Product instance from the ProductVariation ---> {product} and id={product.id} sku={variation.product.sku}")
    logger.debug(f"Product instance from the ProductVariation ---> {product} and id={product.id} sku={product.sku}")

    # If the request method is POST, process the form data
    if request.method == 'POST':
        # Create the forms for both Product and ProductVariation
        product_form = ProductForm(request.POST, instance=product)
        # variation_form = ProductVariationForm(request.POST, instance=variation)

        if product_form.is_valid():

            # To update for product's name and SKU
            # product_name = request.POST.get('product_name', product.name)
            # product_sku = request.POST.get('product_sku', product.sku)

            # Update the product fields with the new values
            # product.name = product_name
            # product.sku = product_sku

            # Save the updated Product data
            product = product_form.save()

            # Save the updated ProductVariation data
            # variation = variation_form.save()

            return redirect('product_list')  # Redirect to the product list page after update

    else:
        # Initialize the forms with the existing data for GET requests
        product_form = ProductForm(instance=product)
        # variation_form = ProductVariationForm(instance=variation)

    # Pass both forms and the related objects to the template
    return render(request, 'myapp/update_product.html', {
        'product_form': product_form,
        # 'variation_form': variation_form,
        'variation': variation,
        'product': product,
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
    writer.writerow(['Product Name', 'Image', 'SKU', 'Quantity', 'Price', 'Color', 'Size', 'Description'])
    
    # Write the data rows
    for variation in variations:
        writer.writerow([variation.product.name, variation.image, variation.product.sku, 
        variation.quantity, variation.price, variation.color.name,
        variation.size.name, variation.product.description ])

    return response

def generate_unique_names(product_name, sku, color, size):
    pass