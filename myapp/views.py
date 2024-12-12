import csv
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductVariation, Color, Size
from .forms import ProductForm, ProductVariationForm, ProductVari_UpdateForm
from django.db.models import Prefetch
from django.http import HttpResponse
import decimal
from django.db.models import Q
import json
from django.core.serializers import serialize
from django.conf import settings
from django.forms.models import model_to_dict

from django.db.models.fields.files import ImageFieldFile

def create_product(request):
    product_form = ProductForm()
    if request.method == 'POST':

        if 'generate' in request.POST:  # Generate button clicked
            
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                # Capture the product name and SKU from the form
                product_name = request.POST.get('name')
                product_sku = request.POST.get('sku')
                color_choices  = request.POST.getlist('color')
                size_choices  = request.POST.getlist('size')
                
                temp_variations = [] # to store combinations temporarily
                request.session['temp_variations'] = temp_variations

                for color_id in color_choices:
                    for size_id in size_choices:
                        try:
                            color = Color.objects.get(id=color_id)
                            size = Size.objects.get(id=size_id)
                            
                            temp_variations.append({
                                'product_name': product_name,
                                'sku': product_sku,
                                'color': color_id,
                                'color_name': color.name,
                                'size': size_id,
                                'size_name':size.name,
                                'quantity': request.POST.get('quantity'),
                                'price': request.POST.get('price'),
                                'image': request.FILES.get('image')
                            })
                        except (Color.DoesNotExist, Size.DoesNotExist):
                            continue
                print(temp_variations)
                # Render the page with the variations, not yet saved to DB
                return render(request, 'myapp/create_product.html', {
                    'product_form': product_form,
                    'variations': temp_variations
                })

        if 'delete_variation' in request.POST:
            product_form = ProductForm(request.POST)
            temp_variations = request.session.get('temp_variations', [])
            # temp_variations.reverse()
            delete_id  = request.POST.get('delete_variation')
            print(f"delete_id ---> {delete_id}")
            delete_id  = int(delete_id) - 1
            # print(delete_id)
            if temp_variations:  # Check if the list is not empty
                temp_variations.pop(delete_id)  
                # temp_variations.reverse()
            # Save the updated list back to the session
            request.session['temp_variations'] = temp_variations
            
            return render(request, 'myapp/create_product.html', {
                    'product_form': product_form,
                    'variations': temp_variations
                })

        if 'save' in request.POST:  # Save button clicked
            temp_variations = request.session.get('temp_variations', [])
            # print(temp_variations)

            
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                # Save the product instance
                product = product_form.save()
                for index,temp_var in enumerate(temp_variations, start=1):
                    quantity = request.POST.get(f'quantity_{index}')
                    price = request.POST.get(f'price_{index}')
                    image = request.FILES.get(f'image_{index}')

                    # Retrieve related objects
                    color = Color.objects.get(id=temp_var['color']) if temp_var['color'] else None
                    size = Size.objects.get(id=temp_var['size']) if temp_var['size'] else None

                    # Create and save the variation
                    ProductVariation.objects.create(
                        product=product,
                        color=color,
                        size=size,
                        quantity=quantity,
                        price=price,
                        image=image,
                    )

                 # Clear session data
                del request.session['temp_variations']
                return redirect('product_list')
            
    else:
        product_form = ProductForm()

    return render(request, 'myapp/create_product.html',
                  {'product_form': product_form,
                    })

# View for Listing Products and their Variations
def product_list(request):
 
    query = request.GET.get('q', '')  # Get the search query from the request (default is an empty string)

    # Filter the queryset using `icontains` to search across multiple fields
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(sku__icontains=query) | Q(description__icontains=query)
    ) if query else Product.objects.all()
    
    if 'export' in request.GET:
        return export_data(products)
    
    context = {
        'products': products,
        'query': query  # Pass the current search query back to the template
    }
    return render(request, 'myapp/product_list.html', context)

def update_product(request, id):
    product = get_object_or_404(Product, id=id)
    colors = Color.objects.all().values('id', 'name', 'code')
    sizes = Size.objects.all().values('id', 'name', 'code')
    added_variations = set()  # Track variations we've already processed
    processed_variations = set()  # Store IDs of processed variations

    product_dict = {
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'description': product.description,
        }
    if request.method == 'POST':
        # Create the product form
        product_form = ProductForm(request.POST, instance=product)
        variations = []
    
        if 'delete' in request.POST:  # Generate button clicked
            delete_product(request, id)
            return redirect("product_list")

        for key, value in request.POST.items():

             # Check if the key contains color and size information
            if key.startswith(('quantity_', 'price_','image_')):  # Tuple for startswith() 
                parts = key.split('_')  # Expecting 'quantity_color_size' structure
                if len(parts) >= 3:
                    field_type, color_name, size_name = parts[:3]  # Unpack parts into field_type, color_name, size_name

                    # Get or create color and size
                    color, _ = Color.objects.get_or_create(name=color_name)
                    size, _ = Size.objects.get_or_create(name=size_name)

                    # Create or update the product variation
                    variation, created = ProductVariation.objects.get_or_create(
                        product=product, 
                        color=color, 
                        size=size,
                        defaults={'quantity': 0, 'price': 0.0, 'image': None}
                    )
                    processed_variations.add(variation.id)

                    # Update the variation fields
                    if field_type == 'quantity':
                        variation.quantity = value
                        file_key = f'image_{color_name}_{size_name}'
                        if file_key in request.FILES:
                            print(f"Yes, '{file_key}' found in request.FILES with value: {request.FILES[file_key]}")
                            variation.image = request.FILES[file_key]
                        else:
                            print(f"No, '{file_key}' not found in request.FILES. Available keys: {list(request.FILES.keys())}")
                    

                    elif field_type == 'price':
                        variation.price = value
                    
                    variation.save()
                    print(f"Save Variation-----------> {variation}")

                    # Use a unique identifier for the variation
                    variation_id = (color.id, size.id)
                    if variation_id not in added_variations:
                        variation_dict = {
                                'color_id': color.id,
                                'color__name': color.name,
                                'color__code': color.code,
                                'id': variation.id,
                                'image': variation.image.url.strip('/media/') if variation.image else None,
                                'price': float(variation.price) if isinstance(variation.price, decimal.Decimal) else variation.price,
                                'product__name': variation.product.name,
                                'product__sku': variation.product.sku,
                                'product_id': variation.product.id,
                                'quantity': variation.quantity,
                                'size_id': size.id,
                                'size__name': size.name,
                                'size__code': size.code,
                        }

                        variations.append(variation_dict)
                        added_variations.add(variation_id)

        # **Delete variations that were not re-included**
        ProductVariation.objects.filter(product=product).exclude(id__in=processed_variations).delete()
        print(f"Deleted all unprocessed variations for product {product.name}")
        
        print(f"New Variations ==> {variations}")
        # Save the product form if valid
        if product_form.is_valid():
            product_form.save()
        return redirect('product_list')

      
    product_form = ProductForm(instance=product)
    variations = ProductVariation.objects.filter(product_id=product.id).values(
            'color', 'color_id', 'color__name', 'color__code', 'id', 'image', 'price',
            'product__name', 'product__sku', 'product_id', 'quantity', 'size', 'size__name',
            'size_id', 'size__code')
        

    # Get selected colors and sizes from query params
    selected_colors = request.GET.getlist('colors', [])  # Colors selected
    selected_sizes = request.GET.getlist('sizes', [])    # Sizes selected

    # Build the filter query
    filter_conditions = Q()

    # If colors are selected, add filter for color
    if selected_colors:
        filter_conditions &= Q(color__id__in=selected_colors)

    # If sizes are selected, add filter for size
    if selected_sizes:
        filter_conditions &= Q(size__id__in=selected_sizes)

    # Apply the filter to the variations queryset if any conditions are present
    if filter_conditions:
        variations = variations.filter(filter_conditions)
    variations = list(variations)  # Convert QuerySet to list
    variations = decimal_and_image_to_serializable(variations)
    print(f"Existing Variations ===> {variations}")

    # Convert ProductVariation instances to dictionaries    

    return render(request, 'myapp/update_product.html', {
            'product_form': product_form,
            'variations': json.dumps(variations),
            'variation_data': variations,
            'product_dict':  json.dumps(product_dict),
            'product': product,
            'MEDIA_URL': settings.MEDIA_URL,
            'colorsobj': json.dumps(list(colors)),
            'sizesobj': json.dumps(list(sizes)),
        })

def decimal_and_image_to_serializable(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: decimal_and_image_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [decimal_and_image_to_serializable(item) for item in obj]
    elif isinstance(obj, ImageFieldFile):  # Handle ImageFieldFile
        return obj.url if obj else None  # Get URL or None if no image is present
    return obj

def delete_variation(request, id): # delete temp generated product
    product_form = ProductForm()

    temp_variations = request.session.get('temp_variations', [])
    if temp_variations:  # Check if the list is not empty
        temp_variations.pop(id-1)  # Remove the first item from the list
    
        # Save the updated list back to the session
        request.session['temp_variations'] = temp_variations
    return render(request, 'myapp/create_product.html', {
        'product_form': product_form,'variations': temp_variations})

def delete_product(request, id): # Delete in list
        
        product = get_object_or_404(Product, id = id)

        # Get the ProductVariation object by ID
        variation = ProductVariation.objects.filter(product=product)
   
        # Delete the ProductVariation
        variation.delete()

        product.delete()

        # Redirect to the product list page
        return redirect('product_list')

def export_data(products):

    print(f"Export data ===> {products}")
    # Prepare the response to download a CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    writer = csv.writer(response)
    
    # Write CSV headers
    writer.writerow(['Product Name', 'SKU', 'Description','Image', 'Quantity', 'Price', 'Color', 'Size' ])
    
    # Write product data
    for product in products:
        writer.writerow([product.name, product.sku, product.description])
        variations = ProductVariation.objects.filter(product=product)  # This gets all variations for each product
        for variation in variations:
            writer.writerow([variation.product.name, variation.product.sku,'', variation.image,  variation.quantity, variation.price, variation.color.name,
            variation.size.name])

    return response

