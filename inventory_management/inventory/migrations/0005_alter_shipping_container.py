# Generated by Django 5.0.4 on 2024-05-13 18:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_alter_gateout_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipping',
            name='container',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.container'),
        ),
    ]
