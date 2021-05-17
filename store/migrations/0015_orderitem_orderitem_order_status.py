# Generated by Django 3.1.4 on 2021-04-19 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_product_view_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='orderItem_order_status',
            field=models.CharField(choices=[('Order Received', 'Order Received'), ('Order Processing', 'Order Processing'), ('On the way', 'On the way'), ('Order Completed', 'Order Completed'), ('Order Canceled', 'Order Canceled')], default='Order Received', max_length=50),
        ),
    ]