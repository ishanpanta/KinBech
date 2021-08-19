from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.views.generic import CreateView, View, DetailView
from django.views.generic.edit import DeleteView, UpdateView
from django.db.models import Sum

from ecommerce.settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from store.models import *
from store.forms import *

import decimal

# SELLER


# Will allows the login user and seller to use the views
class SellerRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated() and Seller.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/sellerLogin/")(reverse_lazy("auth:seller-login"))
        return super().dispatch(request, *args, **kwargs)


# All the graphs
def graphs(request, x_component, y_component, graph_title, xaxis_title, yaxis_title, graph_type="bar"):

    # x and y component
    x = x_component
    y = y_component

    # Bar chart colors
    colors = ['limegreen', 'pink'] * len(x_component)

    # list which contains the trace and layout
    trace_layout_list = []

    # Create a trace json to hold graph data
    trace = {
        'x': x,
        'y': y,
        'type': graph_type,
        'name': x,
        'marker': {'color': colors}
    }

    # appending trace to the list
    trace_layout_list.append(trace)

    # Configure the chart's layout
    layout = {'title': {'text': graph_title,
                        'font': {
                            'color': '#ffffff'}
                        },
              'xaxis': {'title': xaxis_title, 'color': '#DCDCDC', 'mirror': 'true', 'showline': 'false'},
              'yaxis': {'title': yaxis_title, 'color': '#DCDCDC', 'mirror': 'true', 'showline': 'true'},
              'plot_bgcolor': '#38393d', 'paper_bgcolor': '#38393d', 'bordercolor': '#ffffff'}

    # appending layout to the list
    trace_layout_list.append(layout)

    return trace_layout_list


def sellerHome(request):
    a = SellerRequiredMixin()
    seller = request.user.seller

    # orderItems = OrderItem.objects.filter(product__seller=seller, order__order_status="Order Received").order_by("-id")
    orders = Order.objects.filter(orderitem__product__seller=seller, complete=True,
                                  orderitem__orderItem_order_status="Order Received").distinct().order_by("-id")

    # PORTFOLIO PERFORMANCE
    # Total quanity sold till now
    orderItemQuantity = OrderItem.objects.filter(
        product__seller=seller, order__complete=True).aggregate(Sum('quantity'))

    # Total Price
    orderItem = OrderItem.objects.filter(
        product__seller=seller, order__complete=True)

    totalPrice = 0
    for oi in orderItem:
        totalPrice += oi.quantity * oi.product.price

    # END OF PORTFOLIO PERFORMANCE

    # FORM
    graph_selection = ""
    if request.method == 'POST':
        graph_selection = request.POST.get('graph_selection')

        print("Graph selection: ", graph_selection)

    # END OF FORM

    if graph_selection == "" or graph_selection == "totalIncome":

        # # # BAR-CHART (Total Income) # # #

        # list of name, total_quantity and price of ordered products
        orderItem_name = []
        orderItem_total_quantity = []
        orderItem_price = []

        products = Product.objects.filter(seller=seller)

        # adding the total quantity of product sold till now to the above list
        for prod in products:
            orderItems = OrderItem.objects.filter(
                product__seller=seller, product__name=prod.name).aggregate(Sum('quantity'))

            product = Product.objects.get(name=prod)

            # access the aggregate sum of total quantity of the products
            total_product_quantity = orderItems['quantity__sum']

            # if the product has not been sold till now then it wouldnot be added in the list and hence in the graph
            if total_product_quantity == None:
                pass
            else:
                orderItem_name.append(prod.name)
                orderItem_total_quantity.append(total_product_quantity)
                orderItem_price.append(product.price)

        # multiplying two lists (quantity and price) and putting it to the orderItem_total_price_decimal list
        orderItem_total_price_decimal = [quantity * price for quantity,
                                         price in zip(orderItem_total_quantity, orderItem_price)]

        # converting decimal price into float price and further converting to list
        orderItem_total_price = list(map(float, orderItem_total_price_decimal))

        # Calling the graphs function
        # returns the list which contains the trace (1st element) and layout (2nd element)
        trace_layout_list = graphs(request, orderItem_name, orderItem_total_price, graph_title='Total Income',
                                   xaxis_title="Product's Name", yaxis_title='Total Price ($)')

        # title of the graph
        title = "Total Income"

        # # # END OF BAR-CHART (Total Income) # # #

    elif graph_selection == "viewsInProducts":

        # No of views of a product

        # # # BAR-CHART (No of Views) # # #

        # creating a list of all product names with its view_count
        all_product_names = []
        all_product_counts = []

        product_names = Product.objects.filter(seller=seller)

        for product in product_names:
            all_product_names.append(product.name)
            all_product_counts.append(product.view_count)

        trace_layout_list = graphs(request, all_product_names, all_product_counts, graph_title='Number of views in a Product',
                                   xaxis_title="Product's Name", yaxis_title='View Count')

        title = "Number of views in a Product"

        # # # END OF BAR-CHART (No of Views) # # #

    elif graph_selection == "soldProductsQuantity":

        # # # Sold Product's Quantity # # #

        # list of name, total_quantity and price of ordered products
        orderItem_name = []
        orderItem_total_quantity = []

        products = Product.objects.filter(seller=seller)

        # adding the total quantity of product sold till now to the above list
        for prod in products:
            orderItems = OrderItem.objects.filter(
                product__seller=seller, product__name=prod.name).aggregate(Sum('quantity'))

            # access the aggregate sum of total quantity of the products
            total_product_quantity = orderItems['quantity__sum']

            # if the product has not been sold till now then it wouldnot be added in the list and hence in the graph
            if total_product_quantity == None:
                pass
            else:
                orderItem_name.append(prod.name)
                orderItem_total_quantity.append(total_product_quantity)

        # List process THE END

        trace_layout_list = graphs(request, orderItem_name, orderItem_total_quantity, graph_title='Total Quantity Sold',
                                   xaxis_title="Product's Name", yaxis_title='Quantity', graph_type="scatter")

    # # # END OF Sold Product's Quantity # # #

    context = {"orders": orders, "seller": seller,
               'orderItemQuantity': orderItemQuantity, 'totalPrice': totalPrice, "trace": trace_layout_list[0],
               "layout": trace_layout_list[1]}

    return render(request, "seller/sellerHome.html", context)


def sellerProfile(request):
    seller = request.user.seller

    context = {'seller': seller, }
    return render(request, "seller/sellerProfile.html", context)


# class sellerProfileUpdate(UpdateView):
#     template_name = "seller/sellerProfileUpdate.html"
#     queryset = Seller.objects.all()
#     form_class = SellerProfileUpdateForm

#     def get_success_url(self):
#         return reverse_lazy("seller:seller-profile")

def sellerProfileUpdate(request, pk):
    seller = request.user.seller
    form = SellerProfileUpdateForm(instance=seller)
    if request.method == 'POST':
        form = SellerProfileUpdateForm(request.POST, instance=seller)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy("seller:seller-profile"))

    context = {
        "seller": seller,
        "form": form
    }
    return render(request, "seller/sellerProfileUpdate.html", context)


class sellerOrderDetail(DetailView):
    template_name = "seller/sellerOrderDetail.html"

    # sending data from backend to the frontend
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = self.request.user.seller
        order_id = self.kwargs["pk"]

        # change the noti_status of the orderItem
        orderItem_obj = OrderItem.objects.filter(
            order__id=order_id, product__seller=seller)
        for oi in orderItem_obj:
            oi.noti_status = False
            oi.save()

        # contexts
        context["order"] = Order.objects.filter(id=order_id)
        context["orderItems"] = OrderItem.objects.filter(
            order__id=order_id, product__seller=seller)
        context["shippingAddress"] = ShippingAddress.objects.filter(
            order__id=order_id)
        context["allstatus"] = ORDERITEM_ORDER_STATUS
        return context

    def get_queryset(self, **kwargs):
        return Order.objects.filter(id=self.kwargs["pk"])


def sellerOrderList(request):
    seller = request.user.seller
    allorders = Order.objects.filter(
        orderitem__product__seller=seller, complete=True).distinct().order_by("-id")

    orderItem = OrderItem.objects.filter(
        product__seller=seller, order__complete=True).order_by("-id")
    context = {"allorders": allorders, "orderItem": orderItem}
    return render(request, "seller/sellerOrderList.html", context)


def sellerProductList(request):
    seller = request.user.seller
    products = Product.objects.filter(seller=seller).order_by("-id")

    # changing the seller of the products whose seller is empty
    change_product_seller = Product.objects.all()

    for product in change_product_seller:
        if product.seller == None:
            product.seller = seller
            product.save()

    context = {"products": products, }
    return render(request, "seller/sellerProductList.html", context)


class sellerProductAdd(CreateView):
    template_name = "seller/sellerProductAdd.html"
    form_class = ProductForm
    success_url = reverse_lazy("seller:seller-product-list")

    # to save the custom-field in the database
    def form_valid(self, form):
        # created form will be assigned to the variable "product"
        product = form.save()

        images = self.request.FILES.getlist("more_images")
        for image in images:
            ProductImage.objects.create(product=product, image=image)
        return super().form_valid(form)


class sellerOrderStatusChange(View):
    def post(self, request, *args, **kwargs):
        seller = request.user.seller

        # accessing ID of current page.
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)

        new_status = request.POST.get("status")

        # ORDERITEM object
        orderItem_obj = OrderItem.objects.filter(
            order__id=order_id, product__seller=seller)

        # SHIPPING ADDRESS object
        shippingAddress = ShippingAddress.objects.filter(order__id=order_id)

        # NOTE:SEND EMAIL
        subject = "ORDER_#" + str(order_id) + "Order Status: " + new_status

        # defing the message file and passing context
        html_message = render_to_string('seller/emailMessage.html', {'shippingAddress': shippingAddress,
                                                                     'orderItem_obj': orderItem_obj, 'order_obj': order_obj, 'order_id': order_id, 'seller': seller, 'new_status': new_status})
        # striping
        message = strip_tags(html_message)

        # email of the recepient
        recepient = order_obj.customer.user.email

        # creating the email object with all info
        email = EmailMultiAlternatives(
            subject,
            message,
            EMAIL_HOST_USER,
            [recepient],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        # NOTE:END OF SEND EMAIL

        # changing the status of the order
        for orderItem in orderItem_obj:
            if orderItem.orderItem_order_status == "Order Canceled":
                orderItem.orderItem_order_status == "Order Canceled"
                orderItem.save()
            else:
                orderItem.orderItem_order_status = new_status
                orderItem.save()
        return redirect(reverse_lazy("seller:seller-order-detail", kwargs={"pk": order_id}))


def sellerProductDetail(request, slug):
    product = Product.objects.get(slug=slug)

    # DISCOUNT
    discountPrice = 0
    if product.discount > 0.0:
        discountPrice = decimal.Decimal(product.price) - \
            ((decimal.Decimal(product.discount)/decimal.Decimal(100))
             * decimal.Decimal(product.price))

    # Comment AND reply
    comments = ProductComment.objects.filter(
        product=product, parent=None).order_by("-sno")
    replies = ProductComment.objects.filter(
        product=product).exclude(parent=None)

    context = {"product": product, "discountPrice": discountPrice,
               "comments": comments, "replies": replies, }
    return render(request, "seller/sellerProductDetail.html", context)


class sellerProductUpdate(UpdateView):
    template_name = 'seller/sellerProductUpdate.html'
    queryset = Product.objects.all()
    form_class = ProductForm

    def get_success_url(self):
        return reverse_lazy("seller:seller-product-detail", args=[self.kwargs['slug']])


def productDelete(request, pk):
    product = Product.objects.get(id=pk)
    product.delete()
    return redirect(reverse_lazy("seller:seller-product-list"))


def productDisable(request, slug):
    product = Product.objects.get(slug=slug)
    product.disable = True
    product.save()
    return redirect(reverse_lazy("seller:seller-product-detail", args=[slug]))


def productEnable(request, slug):
    product = Product.objects.get(slug=slug)
    product.disable = False
    product.save()
    return redirect(reverse_lazy("seller:seller-product-detail", args=[slug]))

# END OF SELLER
