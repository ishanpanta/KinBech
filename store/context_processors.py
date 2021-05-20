from store.views import cancelOrder
from .models import *


def notification(request):
    if request.user.is_authenticated:
        # seller yo try ma janxa vannu matlab seller jada error aaudaina
        try:
            seller = request.user.seller
        # expect ma chai customer janxa
        except:
            seller = Seller.objects.filter(id=1)
    else:
        seller = Seller.objects.filter(id=1)

    noti_orders = Order.objects.filter(orderitem__product__seller=seller, orderitem__orderItem_order_status="Order Received",
                                       orderitem__noti_status=True, complete=True).distinct().order_by("-id")

    canceledOrderItem = OrderItem.objects.filter(
        product__seller=seller, orderItem_order_status="Order Canceled", noti_status=True)

    return {'noti_orders': noti_orders, 'seller': seller, 'canceledOrderItem': canceledOrderItem}
