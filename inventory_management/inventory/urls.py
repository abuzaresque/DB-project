from django.urls import path
from .views import (
    dashboard, 
    product_view, product_list, 
    box_inventory_view, box_inventory_list,
    open_inventory_view, open_inventory_list,
    gateout_view, gateout_list,
    container_view, container_list,
    shipping_view, shipping_list,
    location, location_view, location_list, get_boxes
)
    
urlpatterns = [

    path('', dashboard, name='dashboard'),
    path('dashboard', dashboard, name='dashboard'),

    # Product URLs
    path('product/', product_view, name='product'),
    path('products/', product_list, name='product_list'),


    path('locations/', location_view, name='location'),
    # path('locations/', location_list, name='location_list'),

    # Box Inventory URLs
    path('box_inventory/', box_inventory_view, name='box_inventory'),
    path('box_inventory_list/', box_inventory_list, name='box_inventory_list'),

    # Open Inventory URLs
    path('open_inventory/', open_inventory_view, name='open_inventory'),
    path('open_inventory_list/', open_inventory_list, name='open_inventory_list'),

    # Gateout URLs
    path('gateout/', gateout_view, name='gateout'),
    path('gateout_list/', gateout_list, name='gateout_list'),

    # Container URLs
    path('container/', container_view, name='container'),
    path('container_list/', container_list, name='container_list'),
    path('api/get_boxes/', get_boxes, name='get_boxes'),

    # Shipping URLs
    path('shipping/', shipping_view, name='shipping'),
    path('shipping_list/', shipping_list, name='shipping_list'),

    path('location/', location, name='location'),
]
