# Generated by Django 5.0.4 on 2024-05-14 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_alter_shipping_shipping_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
