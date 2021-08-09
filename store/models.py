from django.db import models

# Django default User model
from django.contrib.auth.models import User

from django.core.validators import FileExtensionValidator

import decimal


class Seller(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=40, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    image = models.ImageField(null=True, blank=True, validators=[
                              FileExtensionValidator(['png', 'jpg', 'jpeg'])])

    def __str__(self):
        return self.user.username

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = "{% static 'images/user-image.jpg' %}"
        return url


class Customer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=40, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    title = models.CharField(max_length=50, null=True)
    slug = models.SlugField(unique=True, null=True)
    image = models.ImageField(null=True, blank=True, validators=[
                              FileExtensionValidator(['png', 'jpg', 'jpeg'])])

    def __str__(self):
        return self.title

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = "{% static 'images/user-image.jpg' %}"
        return url


class Product(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(unique=True, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    quantity = models.PositiveIntegerField(default=1, null=True)
    brand = models.CharField(max_length=200, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    image = models.ImageField(null=True, blank=True, validators=[
                              FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    description = models.TextField(null=True)
    discount = models.FloatField(default=0)
    warranty = models.CharField(max_length=50, null=True, blank=True)
    return_policy = models.CharField(max_length=60, null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    disable = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    # If user doesnot put an image then it will give us error so to solve this we use this function.
    # we use property decorator so we can access it like an attribute.
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = 'static/images/placeholder.png'
        return url

    @property
    def discount_price(self):
        if self.discount > 0:
            pro_price = decimal.Decimal(self.price) - ((decimal.Decimal(
                self.discount)/decimal.Decimal(100)) * decimal.Decimal(self.price))
            return pro_price

# For adding multiple images for a product


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    image = models.ImageField(null=True, blank=True, validators=[
                              FileExtensionValidator(['png', 'jpg', 'jpeg'])])

    def __str__(self):
        return self.product.name


# Comment on the Products
class ProductComment(models.Model):
    sno = models.AutoField(primary_key=True)
    comment = models.TextField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment[0:13] + "..." + "by" + " " + self.user.username


# Recommendation system
class Recommendation(models.Model):
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, null=True)
    search_product = models.CharField(max_length=100, null=True)
    view_product = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.customer.user.username


# This model will represent a transaction that is placed or pending.
class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, blank=True)

    # 'auto_now_add' field is saved as the current timestamp when a row is first added to the database, and
    #  is therefore perfect for tracking when it was created. This field won’t change again after it’s set.
    date_ordered = models.DateTimeField(auto_now_add=True)

    # complete-False -> This is the open cart. We can continue adding items to the cart.
    # complete-True -> This is the closed cart. We need to create cart for that order.
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    # for total cart price
    @property
    def totalCartPrice(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.totalPrice for item in orderitems])
        return total

    # for total cart quantity
    @property
    def totalCartQuantity(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


ORDERITEM_ORDER_STATUS = (
    ("Order Received", "Order Received"),
    ("Order Processing", "Order Processing"),
    ("On the way", "On the way"),
    ("Order Completed", "Order Completed"),
    ("Order Canceled", "Order Canceled"),
)

# An order Item is one item within an order. A shopping cart may consist of many items but is all part of one order.


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, related_name="product")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    orderItem_order_status = models.CharField(
        max_length=50, choices=ORDERITEM_ORDER_STATUS, default="Order Received")

    # True -> Stored in the notification field
    # False -> Removed from the notification field
    noti_status = models.BooleanField(default=True, null=True, blank=False)

    def __str__(self):
        return self.product.name

    @property
    def totalPrice(self):
        if self.product.discount > 0:
            price = self.product.discount_price * self.quantity
        else:
            price = self.product.price * self.quantity
        return price

# an order can have multiple shippingAddress
# a customer could have multiple shippingAddress


class ShippingAddress(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, related_name="shipping_address")
    address = models.CharField(max_length=50, null=False)
    city = models.CharField(max_length=50, null=False)
    state = models.CharField(max_length=50, null=False)
    zipcode = models.CharField(max_length=50, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
