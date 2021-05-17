from .models import *


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.totalCartQuantity
    else:
        items = []
        order = {'totalCartPrice': 0, 'totalCartQuantity': 0}
        cartItems = order['totalCartQuantity']

    return {'cartItems': cartItems, 'order': order, 'items': items}
