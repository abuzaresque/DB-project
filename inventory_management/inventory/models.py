from django.db import models

class WarehouseLocation(models.Model):
    location_name = models.CharField(max_length=100, primary_key=True)


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    size = models.CharField(max_length=100)
    colour = models.CharField(max_length=100)
    detail = models.TextField()

class BoxInventory(models.Model):
    box_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    q_per_box = models.IntegerField()
    no_of_box = models.IntegerField()
    location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE)


class OpenInventory(models.Model):
    open_inventory_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.product.name} __ {self.location.location_name} __ {self.quantity}"

class Gateout(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(OpenInventory, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE)
    to = models.CharField(max_length=255)
    date = models.DateField()

class Container(models.Model):
    container_number = models.AutoField(primary_key=True)
    date = models.DateField()
    box = models.ForeignKey(BoxInventory, on_delete=models.CASCADE)
    no_of_box = models.IntegerField()
    from_location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE)
    to_location = models.CharField(max_length=255)

class Shipping(models.Model):
    shipping_id = models.AutoField(primary_key=True)
    container = models.ForeignKey(Container,to_field='container_number' , on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
