from django import forms
from .models import Product, BoxInventory, OpenInventory, Gateout, Container, Shipping, WarehouseLocation

class LocationForm(forms.ModelForm):
    class Meta:
        model = WarehouseLocation
        fields = ['location_name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'size', 'colour', 'detail']

class BoxInventoryForm(forms.ModelForm):
    class Meta:
        model = BoxInventory
        fields = [ 'product', 'q_per_box', 'no_of_box', 'location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.all()

    def label_from_instance(self, obj):
        return obj.name

class OpenInventoryForm(forms.ModelForm):
    class Meta:
        model = OpenInventory
        fields = ['product', 'quantity', 'location']
    
    def label_from_instance(self, obj):
        return obj.name

class GateoutForm(forms.ModelForm):
    class Meta:
        model = Gateout
        fields = ['product', 'quantity', 'to', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(GateoutForm, self).__init__(*args, **kwargs)
        # Customize the product field queryset to include OpenInventory instances
        open_inventory_options = OpenInventory.objects.all()
        self.fields['product'].queryset = open_inventory_options

        # Customize the product field choices to display OpenInventory attributes
        self.fields['product'].widget.choices = [
            (open_inventory.open_inventory_id, f"{open_inventory.product.name} - {open_inventory.location.location_name} - {open_inventory.quantity}")
            for open_inventory in open_inventory_options
        ]
    
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        product = self.cleaned_data['product']
        product_id = product.open_inventory_id  # Extract the ID from the OpenInventory object
        open_inventory = OpenInventory.objects.get(pk=product_id)
        if quantity > open_inventory.quantity:
            raise forms.ValidationError("Quantity should not exceed available quantity in inventory.")
        return quantity
    
    def save(self, commit=True):
        instance = super(GateoutForm, self).save(commit=False)
        quantity = self.cleaned_data['quantity']
        product = self.cleaned_data['product']
        open_inventory = product  # Rename for clarity
        open_inventory.quantity -= quantity  # Subtract the quantity
        open_inventory.save()  # Save the updated OpenInventory record
        instance.location = open_inventory.location  # Set the location
        if commit:
            instance.save()
        return instance


class ContainerForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = ['date', 'box', 'no_of_box', 'from_location', 'to_location']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['container_number'].queryset = Container.objects.all()
        self.fields['box_id'].queryset = BoxInventory.objects.none()
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['box'].label = 'Box'
        self.fields['from_location'].label = 'Warehouse'

    def filter_boxes_by_location(self, location_id):
        if location_id:
            self.fields['box'].queryset = BoxInventory.objects.filter(location=location_id)
        else:
            self.fields['box'].queryset = BoxInventory.objects.none()

class ShippingForm(forms.ModelForm):
    class Meta:
        model = Shipping
        fields = ['container', 'timestamp', 'latitude', 'longitude']
