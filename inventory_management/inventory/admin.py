from django.contrib import admin
from .models import Product, BoxInventory, OpenInventory, Gateout, Container, Shipping

# Register your models here.
admin.site.register(Product)
admin.site.register(BoxInventory)
admin.site.register(OpenInventory)
admin.site.register(Gateout)
admin.site.register(Container)
admin.site.register(Shipping)
