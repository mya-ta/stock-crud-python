import csv
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductVariation, Color, Size
from .forms import ProductForm, ProductVariationForm, ProductVari_UpdateForm
from django.db.models import Prefetch
from django.http import HttpResponse


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
    # Fetch product variations with related Product, Color, and Size objects
    products = Product.objects.all().order_by('-id')
    return render(request, 'myapp/product_list.html', {'products': products})

def child_list(request):
    # Fetch product variations with related Product, Color, and Size objects
    product_variations = ProductVariation.objects.select_related(
        'product', 'color', 'size'
    ).order_by('-product_id')

    return render(request, 'myapp/child_list.html', {'product_variations': product_variations})

def update_product(request, id, category):
  
    if category == 'child' : 
        variation = get_object_or_404(ProductVariation, id=id)
        product = variation.product
        if request.method == "POST":
            product_form = ProductForm(request.POST, instance=product)
            productVari_form = ProductVariationForm(request.POST, request.FILES, instance=variation)
            if product_form.is_valid() and productVari_form.is_valid():
                
                # Save the updated Product data
                product = product_form.save()
 
                new_image = request.FILES.get('image', None)
                if new_image:
                    variation.image = new_image
                variation.price = productVari_form.cleaned_data.get('price', variation.price)
                variation.quantity = productVari_form.cleaned_data.get('quantity', variation.quantity)
                variation.save() # Save the updated fields in ProductVariation (only these fields)
                return redirect('child_list')  # Redirect to the product list page after update
            else:
                # Log errors for debugging
                print(product_form.errors)
                print(productVari_form.errors)
        else:
            product_form = ProductForm(instance=product)
            productVari_form = ProductVariationForm(instance=variation)

    else: # if category == 'parent' : 
        product = get_object_or_404(Product, id=id)
        if request.method == 'POST' :
            # Create the forms for both Product and ProductVariation
            product_form = ProductForm(request.POST, instance=product)
    
            if product_form.is_valid():
                product = product_form.save()
                return redirect('product_list')
            else:
                print(product_form.errors)
        else: 
            product_form = ProductForm(instance=product)
            productVari_form = []
            variation = []
    return render(request, 'myapp/update_product.html', {
        'product_form': product_form,
        'productVari_form': productVari_form,
        'variation': variation,
        'product': product,
        'category': category
    })

def delete_variation(request, id): # delete temp generated product
    product_form = ProductForm()

    temp_variations = request.session.get('temp_variations', [])
    if temp_variations:  # Check if the list is not empty
        temp_variations.pop(id-1)  # Remove the first item from the list
    
        # Save the updated list back to the session
        request.session['temp_variations'] = temp_variations
    return render(request, 'myapp/create_product.html', {
        'product_form': product_form,'variations': temp_variations})

def delete_product(request, id, category): # Delete in list

    if category == "parent":
        product = get_object_or_404(Product, id = id)
        product.delete()
        return redirect ('product_list')

    else: 
        # Get the ProductVariation object by ID
        variation = get_object_or_404(ProductVariation, id=id)
    
        # Delete the ProductVariation
        variation.delete()
    
        # Redirect to the product list page
        return redirect('child_list')

def search_product(request):
    variations = ''
    search_name = ''
    search_color = []
    search_size = []
    result = ''

    if request.method == "POST":
        if 'cancel' in request.POST:
            return render(request, 'myapp/search_product.html', {
                'variations': '',
                'product_form': ProductForm(),
                'search_name': '',
                'search_color': [],
                'search_size': [],
            })
        
        search_name = request.POST.get('search_name', '')
        search_color = request.POST.getlist('search_color', [])
        search_size = request.POST.getlist('search_size', [])

        variations = ProductVariation.objects.all()

        if search_name:
            variations = variations.filter(product__name__icontains=search_name)
        
        if search_color:
            variations = variations.filter(color__id__in=search_color)

        if search_size:
            variations = variations.filter(size__id__in=search_size)
        
        print(f"Before variation -> {variations}")

        serialized_variations = list(variations.values('product__name', 'image', 'product__sku', 'quantity', 'price', 
        'color__name', 'size__name', 'product__description'))

        request.session['search_results'] = serialized_variations

        if variations: 
            result = True
        else:
            result = False

    return render(request, 'myapp/search_product.html', {
        'variations': variations,
        'product_form': ProductForm(),
        'search_name': search_name,
        'search_color': search_color,
        'search_size': search_size,
        'result': result,
    })

    # # Serialize the variations queryset to a list of dictionaries (JSON format)
    # serialized_variations = list(variations.values(
    #     'product__name', 'image', 'product__sku', 'quantity', 'price', 
    #     'color__name', 'size__name', 'product__description'
    # ))

    # # Store the serialized results in the session
    # request.session['search_results'] = serialized_variations

def export_data(request): # for all
  
    products = Product.objects.all()  # This fetches all Product objects

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_products.csv"'

    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow(['Product Name', 'SKU', 'Description','Image', 'Quantity', 'Price', 'Color', 'Size' ])
    
    # Write the data rows
    for product in products:
        writer.writerow([product.name, product.sku, product.description])
        variations = product.variations.all()  # This gets all variations for each product
        for variation in variations:
            writer.writerow([variation.product.name, variation.product.sku,'', variation.image,  variation.quantity, variation.price, variation.color.name,
            variation.size.name])

    return response

def export_csv(request): # for searched results

    variations = request.session.get('search_results', [])
    print(f"After variation -> {variations}")

    # # Serialize the variations queryset to a list of dictionaries (JSON format)
    

    if not variations:
        return HttpResponse("No data to export", status=400)
    
    # Create the HTTP response with the CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="product_variations.csv"'

    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow(['Product Name', 'Image', 'SKU', 'Quantity', 'Price', 'Color', 'Size'])
    # Write the data rows
    for variation in variations:
        writer.writerow([variation['product__name'], variation['image'], variation['product__sku'], 
                         variation['quantity'], variation['price'], variation['color__name'],
                         variation['size__name']])

    # Write the data rows
    # for variation in variations:
    #     writer.writerow([variation.product.name, variation.image, variation.product.sku, 
    #     variation.quantity, variation.price, variation.color.name,
    #     variation.size.name, variation.product.description ])

    return response
