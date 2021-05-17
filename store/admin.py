from django.contrib import admin

from .models import *

admin.site.register(Seller)
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductComment)
admin.site.register(Recommendation)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
