from django.shortcuts import render, redirect
from .models import Product, BoxInventory, OpenInventory, Gateout, Container, Shipping, WarehouseLocation
from .forms import ProductForm, BoxInventoryForm, OpenInventoryForm, GateoutForm, ContainerForm, ShippingForm, LocationForm
from django.utils import timezone
from django.http import HttpResponse

from django.db.models import Count, Sum


import plotly.graph_objs as go
from plotly.offline import plot

def dashboard(request):
    total_products = Product.objects.count()
    total_open_inventory = OpenInventory.objects.count()
    total_gateouts = Gateout.objects.count()
    total_containers = Container.objects.count()
    total_shipments = Shipping.objects.count()

    # Calculate product distribution based on quantities in open inventory
    product_distribution = OpenInventory.objects.values('product__name').annotate(total_quantity=Sum('quantity'))

    # Extract product names and their respective total quantities
    product_names = [item['product__name'] for item in product_distribution]
    total_quantities = [item['total_quantity'] for item in product_distribution]

    # Create a bar chart using Plotly
    fig = go.Figure(data=[go.Bar(x=product_names, y=total_quantities, width= 0.25)])
    fig.update_layout(title='Product Distribution based on Quantities in Open Inventory',
                      xaxis_title='Product',
                      yaxis_title='Total Quantity')
    
    # Convert the figure to HTML to embed in the template
    chart_html = plot(fig, output_type='div')

    return render(request, 'dashboard.html', {
        'total_products': total_products,
        'total_open_inventory': total_open_inventory,
        'total_gateouts': total_gateouts,
        'total_containers': total_containers,
        'total_shipments': total_shipments,
        'product_distribution': product_distribution,
        'chart_html': chart_html,
    })






def warehouse_view(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            form = redirect('warehouse_list')  # Redirect to a page showing the list of locations
    else:
        form = LocationForm()
    return render(request, 'warehouse_form.html', {'form': form})

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

def warehouse_list(request):
    query = request.GET.get('q', '')
    locations = WarehouseLocation.objects.filter(location_name__icontains=query)
    return render(request, 'warehouse_list.html', {'locations': locations})

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
    shipments = Shipping.objects.filter(container__container_number__icontains=query)
    return render(request, 'shipping_list.html', {'shipments': shipments})


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

YOUR_RECEIVED_LATITUDEa  = 0
YOUR_RECEIVED_LONGITUDEa = 0

@csrf_exempt
def location(request):
    if request.method == 'POST':
        try:
            print("connection established")
            data = json.loads(request.body.decode('utf-8'))
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            # con
            container = Container.objects.get(container_number = 4)


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
        latest_shipping = Shipping.objects.order_by('-timestamp').last()
        print(latest_shipping)

        if latest_shipping:
            latitude = latest_shipping.latitude
            longitude = latest_shipping.longitude

            context = {
                'latitude': latitude,
                'longitude': longitude,
            }
            return render(request, 'shipping_tracking.html', context)
        else:
            # If no shipping records exist, provide default coordinates
            context = {
                'latitude': 0.0,
                'longitude': 0.0,
            }
            return render(request, 'shipping_tracking.html', context)
    return render(request, 'shipping_tracking.html', context)
    


from .models import Product, BoxInventory, OpenInventory, Gateout
