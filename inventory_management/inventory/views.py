from django.shortcuts import render, redirect
from .models import Product, BoxInventory, OpenInventory, Gateout, Container, Shipping, WarehouseLocation
from .forms import ProductForm, BoxInventoryForm, OpenInventoryForm, GateoutForm, ContainerForm, ShippingForm, LocationForm
from django.utils import timezone
from django.http import HttpResponse

def dashboard(request):
    # Query the database to retrieve the five most recent gateouts
    recent_bgateouts = (BGateout.objects.annotate(max_date=Max('gateout_date'))
                        .values('b_gateout_id', 'box_id', 'gateout_date', 'from_location__location_name', 'to_location')
                        .order_by('-max_date')[:5])
    recent_ogateouts = (OGateout.objects.annotate(max_date=Max('gateout_date'))
                        .values('o_gateout_id', 'o_product_id', 'gateout_date', 'from_location__location_name', 'to_location')
                        .order_by('-max_date')[:5])

    recent_gateouts = list(recent_bgateouts) + list(recent_ogateouts)


        # Query OProducts sales data
    oproducts_sales = (OGateout.objects.select_related('o_product_id')
                       .annotate(sale_date=TruncDay('gateout_date'))
                       .values('sale_date')
                       .annotate(sales_count=Count('o_product_id'))
                       .order_by('sale_date'))
    
    # Query BProducts sales data
    bproducts_sales = (BGateout.objects.select_related('box_id__b_product_id')
                       .annotate(sale_date=TruncDay('gateout_date'))
                       .values('sale_date')
                       .annotate(sales_count=Count('box_id__b_product_id'))
                       .order_by('sale_date'))

    # Prepare the data for Chart.js
    oproducts_data = [{'sale_date': data['sale_date'].strftime('%Y-%m-%d'), 'sales_count': data['sales_count']} for data in oproducts_sales]
    bproducts_data = [{'sale_date': data['sale_date'].strftime('%Y-%m-%d'), 'sales_count': data['sales_count']} for data in bproducts_sales]

    sidebar_closed = False  # Set this variable based on your conditions
    context = {
        'recent_gateouts': recent_gateouts,
        'oproducts_data': oproducts_data,
        'bproducts_data': bproducts_data,
        'sidebar_closed': sidebar_closed
    }

    return render(request, 'dashboard.html', context)


def location_view(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            form = redirect('location')  # Redirect to a page showing the list of locations
    else:
        form = LocationForm()
    return render(request, 'location.html', {'form': form})

# View for adding/editing products
def product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

# View for managing box inventory
def box_inventory_view(request):
    if request.method == 'POST':
        form = BoxInventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('box_inventory_list')
    else:
        form = BoxInventoryForm()
    return render(request, 'box_inventory_form.html', {'form': form})

# View for managing open inventory
def open_inventory_view(request):
    if request.method == 'POST':
        form = OpenInventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('open_inventory_list')
    else:
        form = OpenInventoryForm()
    return render(request, 'open_inventory_form.html', {'form': form})



# View for processing gateout operations
def gateout_view(request):
    if request.method == 'POST':
        form = GateoutForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gateout_list')
    else:
        form = GateoutForm()
    return render(request, 'gateout_form.html', {'form': form})


from django.db.models import Max
# View for managing containers
def container_view(request):
    if request.method == 'POST':
        form = ContainerForm(request.POST)
        if form.is_valid():

            from_location = form.cleaned_data['from_location']  # Get the selected location name text
            
            date = form.cleaned_data['date']
            to_location = form.cleaned_data['to_location']
            box = form.cleaned_data['box']
            no_of_box = form.cleaned_data['no_of_box']


            try:
                box_inventory = BoxInventory.objects.get(location=from_location, box_id=box.box_id)
                if box_inventory.no_of_box >= no_of_box:
                    box_inventory.no_of_box -= no_of_box
                    box_inventory.save()
                else:
                    # Handle case where no_of_box entered is greater than available no_of_box
                    print("No enough boxes available")
                    return HttpResponse("No enough boxes available", status=400)
            except BoxInventory.DoesNotExist:
                # Handle case where there is no BoxInventory entry for the selected product and location
                print("Box inventory entry not found")
                return HttpResponse("Box inventory entry not found", status=400)


            container = Container(
            date = date,
            box =box,
            no_of_box =no_of_box,
            from_location = from_location,
            to_location = to_location, 
            )
            
            container.save()

            print("Box saved")


            return redirect('container_list') 
        
        else:
            print("form invalid",form.errors)

    else:
        form = ContainerForm()

    locations = WarehouseLocation.objects.all()
    containers = Container.objects.all()
    print(containers)

    return render(request, 'container_form.html', {'form': form,  'locations': locations, 'containers': containers})


def get_boxes(request):
    location_id = request.GET.get('location_id')
    print('Location: ',location_id)
    boxes = BoxInventory.objects.filter(location=location_id).select_related('product')
    data = []
    for box in boxes:
        data.append({
            'box_id': box.box_id,
            'product_name': box.product.name
        })

    print(data)

    return JsonResponse(data, safe=False)




# View for managing shipping details
def shipping_view(request):
    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shipping_list')
    else:
        form = ShippingForm()
    return render(request, 'shipping_form.html', {'form': form})

def location_list(request):
    query = request.GET.get('q', '')
    locations = WarehouseLocation.objects.filter(name__icontains=query)
    return render(request, 'location_list.html', {'locations': locations})

def product_list(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query)
    return render(request, 'product_list.html', {'products': products})

def box_inventory_list(request):
    query = request.GET.get('q', '')
    boxes = BoxInventory.objects.filter(product__name__icontains=query)
    return render(request, 'box_inventory_list.html', {'boxes': boxes})


def open_inventory_list(request):
    query = request.GET.get('q', '')
    inventory = OpenInventory.objects.filter(product__name__icontains=query)
    return render(request, 'open_inventory_list.html', {'inventory': inventory})

def gateout_list(request):
    query = request.GET.get('q', '')
    gateouts = Gateout.objects.filter(product__product__name__icontains=query)
    return render(request, 'gateout_list.html', {'gateouts': gateouts})

def container_list(request):
    query = request.GET.get('q', '')
    containers = Container.objects.filter(container_number__icontains=query)
    return render(request, 'container_list.html', {'containers': containers})

def shipping_list(request):
    query = request.GET.get('q', '')
    shippings = Shipping.objects.filter(container__container_number__icontains=query)
    return render(request, 'shipping_list.html', {'shippings': shippings})


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

YOUR_RECEIVED_LATITUDEa  = 0
YOUR_RECEIVED_LONGITUDEa = 0

@csrf_exempt
def location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            # con
            container = Container.objects.get(container_number = 2)


            shipping = Shipping.objects.create(
                container = container,
                timestamp=timezone.now(),
                latitude=latitude,
                longitude=longitude
            )

            # Save the Shipping object
            shipping.save()
            
            # Do something with the location data
            print(f"Received location - Latitude: {latitude}, Longitude: {longitude}")
            
            # Return a JSON response indicating success
            return JsonResponse({'message': 'Location data received successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
    elif request.method == 'GET':
        # Retrieve the latest shipping record from the database
        latest_shipping = Shipping.objects.order_by('-timestamp').first()

        if latest_shipping:
            latitude = latest_shipping.latitude
            longitude = latest_shipping.longitude

            context = {
                'latitude': latitude,
                'longitude': longitude,
            }
            return render(request, 'shipping_list.html', context)
        else:
            # If no shipping records exist, provide default coordinates
            context = {
                'latitude': 0.0,
                'longitude': 0.0,
            }
            return render(request, 'shipping_list.html', context)
    return render(request, 'shipping_list.html', context)
    


# def show_map(request):
#     latitude = YOUR_RECEIVED_LATITUDE  # Replace with actual latitude received from React Native
#     longitude = YOUR_RECEIVED_LONGITUDE  # Replace with actual longitude received from React Native
#     context = {
#         'latitude': latitude,
#         'longitude': longitude,
#     }
#     return render(request, 'maps.html', context)


# def show_map(request):
#     if request.method == 'GET':
#         # Retrieve the latest shipping record from the database
#         latest_shipping = Shipping.objects.order_by('-timestamp').first()

#         if latest_shipping:
#             latitude = latest_shipping.latitude
#             longitude = latest_shipping.longitude

#             context = {
#                 'latitude': latitude,
#                 'longitude': longitude,
#             }
#             return render(request, 'maps.html', context)
#         else:
#             # If no shipping records exist, provide default coordinates
#             context = {
#                 'latitude': 0.0,
#                 'longitude': 0.0,
#             }
#             return render(request, 'maps.html', context)
#     else:
#         return JsonResponse({'error': 'Method not allowed'}, status=405)