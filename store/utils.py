from .models import *
import json


def cookieCart(request):
    try:
        # access COOKIES
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    items = []
    order = {'totalCartPrice': 0, 'totalCartQuantity': 0}
    cartItems = order['totalCartQuantity']

    # add all the quantity of the products in cookies
    for i in cart:
        # We use try block to prevent items in cart that may have been removed from causing error
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            # total amount and total quantity to be displayed in the cart page
            order['totalCartPrice'] += total
            order['totalCartQuantity'] += cart[i]['quantity']

            # build cart items
            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
                },
                'quantity': cart[i]['quantity'],
                'totalPrice': total,
            }
            items.append(item)

        except:
            pass

    return {'cartItems': cartItems, 'order': order, 'items': items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.totalCartQuantity

        # COOKIES
        # displaying the total number of items in cart present
        try:
            # access COOKIES
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}

        if cart != None:
            for i in cart:

                product = Product.objects.get(id=i)

                if product.quantity >= cart[i]['quantity']:
                    cartItems += cart[i]['quantity']

                # if the product quantity is less than the orderItem quantity then the quantity will be
                #  product quantity not orderItem quantity
                else:
                    cartItems += product.quantity

        # END OF COOKIES

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems': cartItems, 'order': order, 'items': items}
