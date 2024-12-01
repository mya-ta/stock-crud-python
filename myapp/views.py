import csv
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductVariation, Color, Size
from .forms import ProductForm, ProductVariationForm, ProductVari_UpdateForm
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
                print(f"color={color_choices}/ size={size_choices}")

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

    print(f"Ans ---> Product: {product} and id={product.id} sku={variation.product.sku}")

    # If the request method is POST, process the form data
    if request.method == 'POST':
        # Create the forms for both Product and ProductVariation
        product_form = ProductForm(request.POST, instance=product)
        # productVari_form = ProductVariationForm(request.POST, request.FILES, instance=variation)
        productVari_form = ProductVari_UpdateForm(request.POST, request.FILES)

        print("Colors --> ", variation.color.id, "color instance -->", Color.objects.get(id=variation.color.id))

        # color = get_object_or_404(Color, id=color_id)
        # size = get_object_or_404(Size, id=size_id)        

        if product_form.is_valid() and productVari_form.is_valid():
            # To update for product's name and SKU
            # product_name = request.POST.get('product_name', product.name)
            # product_sku = request.POST.get('product_sku', product.sku)

            # Save the updated Product data
            product = product_form.save()

            # ProductVariation.objects.filter(id=id).update(price=variation.price, quantity=variation.quantity, image=variation.image)
                
            # variation.save(commit=False)
            # variation.color_id = variation.color.id
            # variation.image = productVari_form.cleaned_data.get('image', variation.image)
            # variation.quantity = productVari_form.cleaned_data.get('quantity', variation.quantity)
            # variation.price = productVari_form.cleaned_data.get('price', variation.price)
            # productVari_form.save(update_fields=['product', 'image', 'quantity', 'price'])
            # variation = productVari_form.save()

            # variation.save(commit=False)
            # # Update only the specific fields in ProductVariation (image, price, and quantity)
            print("Image --> ", productVari_form.cleaned_data.get('image', variation.image))
            new_image = request.FILES.get('image', None)
            if new_image:
                variation.image = new_image
            # variation.image = productVari_form.cleaned_data.get('image', variation.image)
            variation.price = productVari_form.cleaned_data.get('price', variation.price)
            variation.quantity = productVari_form.cleaned_data.get('quantity', variation.quantity)

            # print("Price --> ", productVari_form.cleaned_data.get('price', variation.price))
            
            variation.save() # Save the updated fields in ProductVariation (only these fields)

            # Save the updated Product data
            # product = product_form.save()
            # variation = variation_form.save()

            # Save the updated ProductVariation
            # variation.quantity = productVari_form.cleaned_data['quantity']
            # variation.price = productVari_form.cleaned_data['price']
            # variation.image = productVari_form.cleaned_data['image']
            # variation = productVari_form.save()
            # productVari_form.save(update_fields=['quantity', 'price', 'image'])
            
            return redirect('product_list')  # Redirect to the product list page after update
        else:
            # Log errors for debugging
            print("Error --->", product_form.errors)
            print(productVari_form.errors)
    else:
        # Initialize the forms with the existing data for GET requests
        product_form = ProductForm(instance=product)
        productVari_form = ProductVariationForm(instance=variation)

    # Pass both forms and the related objects to the template
    return render(request, 'myapp/update_product.html', {
        'product_form': product_form,
        'productVari_form': productVari_form,
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
    search_color = request.POST.getlist('search_color', '')
    search_size = request.POST.getlist('search_size', '')

    # Filter the ProductVariation model based on the search criteria
    variations = ProductVariation.objects.all()

    if search_name:
        variations = variations.filter(product__name__icontains=search_name)
    if search_color:
        # variations = variations.filter(color__name__icontains=search_color)
        # variations = variations.filter(color__id__icontains=color_id)
        variations = variations.filter(color__id__in=search_color)

    if search_size:
        variations = variations.filter(size__id__in=search_size)

    # Serialize the variations queryset to a list of dictionaries (JSON format)
    serialized_variations = list(variations.values(
        'product__name', 'image', 'product__sku', 'quantity', 'price', 
        'color__name', 'size__name', 'product__description'
    ))

    # Store the serialized results in the session
    request.session['search_results'] = serialized_variations

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
    # if 'export_csv' in request.POST:
    #     search_name = request.POST.get('search_name', '')
    #     search_color = request.POST.getlist('search_color', '')
    #     search_size = request.POST.getlist('search_size', '')

    # print (f"name: {search_name}/ color: {search_color}/ size: {search_size}")

    # # Filter the ProductVariation model based on the search criteria
    # variations = ProductVariation.objects.all()

    # if search_name:
    #     variations = variations.filter(product__name__icontains=search_name)
    # if search_color:
    #     variations = variations.filter(color__id__in=search_color)
    # if search_size:
    #     variations = variations.filter(size__id__in=search_size)

    # Retrieve the serialized variations from the session
    serialized_variations = request.session.get('search_results', [])

    if not serialized_variations:
        return HttpResponse("No data to export", status=400)
    
    # Create the HTTP response with the CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="product_variations.csv"'

    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow(['Product Name', 'Image', 'SKU', 'Quantity', 'Price', 'Color', 'Size', 'Description'])
    # Write the data rows
    for variation in serialized_variations:
        writer.writerow([variation['product__name'], variation['image'], variation['product__sku'], 
                         variation['quantity'], variation['price'], variation['color__name'],
                         variation['size__name'], variation['product__description']])

    # Write the data rows
    # for variation in variations:
    #     writer.writerow([variation.product.name, variation.image, variation.product.sku, 
    #     variation.quantity, variation.price, variation.color.name,
    #     variation.size.name, variation.product.description ])

    return response

def generate_unique_names(product_name, sku, color, size):
    pass