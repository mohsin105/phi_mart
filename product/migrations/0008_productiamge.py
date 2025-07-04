# Generated by Django 5.1.7 on 2025-06-18 16:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_remove_review_date_review_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductIamge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='', verbose_name='products/images/')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='product.product')),
            ],
        ),
    ]
