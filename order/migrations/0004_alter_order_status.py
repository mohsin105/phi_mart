# Generated by Django 5.1.7 on 2025-03-20 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_alter_cartitem_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Not Paid', 'Not Paid'), ('Ready To Ship', 'Ready To Ship'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Canceled', 'Canceled')], default='Not Paid', max_length=20),
        ),
    ]
