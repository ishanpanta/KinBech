from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, View, DetailView

from django.db.models import Q, Sum
from django.core.paginator import Paginator

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.views.generic.edit import DeleteView, UpdateView

from .models import *
from .forms import *
from .utils import cartData
from operator import itemgetter
import datetime
import decimal
import json


# Registration
class CustomerRegistrationView(CreateView):
    template_name = "store/customerRegistration.html"
    form_class = customerRegistrationForm
    success_url = reverse_lazy("app:customer-login")

    def form_valid(self, form):
        # display success message after the Registration
        uname = form.cleaned_data.get("username")
        messages.success(self.request, 'Account was created for ' + uname)

        user = User.objects.create_user(
            form.cleaned_data.get("username"),
            email=form.cleaned_data.get("email"),
            password=form.cleaned_data.get("password1"),
        )

        # form.instance is the customer instance. To supply user as a value:
        form.instance.user = user

        return super().form_valid(form)


# Login
def customerLogin(request):

    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None and Customer.objects.filter(user__username=username).exists():
            login(request, user)
            return redirect("app:store")
        else:
            messages.info(request, "Username OR Password is incorrect")

    return render(request, "store/customerLogin.html", {})


# Logout
def customerLogout(request):
    logout(request)
    return redirect("app:store")


# to show the content in the templates in the django page.
def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    # RECOMMENDATION
    if request.user.is_authenticated:
        customer = request.user.customer

        # creating Recommendation for each customer
        Recommendation.objects.get_or_create(customer=customer)

        # at the first visit the search and vist product will be null so to prevent the error
        try:
            # getting the recommended products name
            recommend = Recommendation.objects.get(customer=customer)
            search_product = recommend.search_product
            view_product = recommend.view_product
            # print("Searched Product: ", search_product)
            # print("View Product: ", view_product)

            # Category of searched product
            try:
                # getting the category name of the search_product
                get_searchedPro_category = Category.objects.filter(
                    Q(product__name__icontains=search_product) | Q(product__description__icontains=search_product) | Q(title__icontains=search_product))[0]
                # print("Search Cate: ", get_searchedPro_category)
            except:
                get_searchedPro_category = None
                # print("Search Cate: ", get_searchedPro_category)

            # Category of viewed product
            try:
                # getting the category name of the view_product
                get_viewedPro_category = Category.objects.filter(
                    Q(product__name__icontains=view_product))[0]
                # print("View cate: ", get_viewedPro_category)
            except:
                get_viewedPro_category = None
                # print("View cate: ", get_viewedPro_category)

            # if searched and viewed category are equal then send only one querset and set another to none
            if get_searchedPro_category == get_viewedPro_category:
                recom_searched_products = Product.objects.filter(
                    Q(category__title__icontains=get_searchedPro_category), disable=False).order_by("-view_count")
                recom_viewed_products = None

            else:
                # if there is any searched category then it will send querset else it will send None
                try:
                    recom_searched_products = Product.objects.filter(
                        Q(category__title__icontains=get_searchedPro_category), disable=False).order_by("-view_count")
                except:
                    recom_searched_products = None

                # same
                try:
                    recom_viewed_products = Product.objects.filter(
                        Q(category__title__icontains=get_viewedPro_category), disable=False).order_by("-view_count")
                except:
                    recom_viewed_products = None

        except:
            recom_searched_products = None
            recom_viewed_products = None

    else:
        recom_searched_products = None
        recom_viewed_products = None

    # print(recom_searched_products)
    # print(recom_viewed_products)

    # END OF RECOMMENDATION

    # getting all the categories
    categories = Category.objects.all()

    # MOST VIEWED products
    most_viewed_products = Product.objects.all().order_by("-view_count")

    # The end OF MOST VIEWED

    # BEST SELLING products

    # list of name, total_quantity and price of ordered products
    orderItem_name = []
    orderItem_total_quantity = []

    products = Product.objects.all()

    # adding the total quantity of product sold till now to the above list
    for prod in products:
        orderItems = OrderItem.objects.filter(
            product__name=prod.name).aggregate(Sum('quantity'))

        # access the aggregate sum of total quantity of the products
        total_product_quantity = orderItems['quantity__sum']

        # if the product has not been sold till now then it wouldnot be added in the list and hence in the graph
        if total_product_quantity == None:
            pass
        else:
            orderItem_name.append(prod.name)
            orderItem_total_quantity.append(total_product_quantity)

    # 2-D list formed of orderItem_name and orderItem_total_quantity
    orderItem_name_quantity_2D = list(
        zip(orderItem_name, orderItem_total_quantity))

    # sorting according to highest quantity
    orderItem_name_quantity_2D.sort(key=itemgetter(1), reverse=True)

    # THE END OF BEST SELLING products

    # to hide best_seller_products if there is no order till now
    orderItems = OrderItem.objects.all()

    # COOKIES
    # setting cookies items to the database
    if request.user.is_authenticated:

        # access CART cookie
        try:
            cart = json.loads(request.COOKIES['cart'])
            print("CART aayo: ", cart)
        except:
            cart = {}

        # sending all the cookie items to the createUpdateOrder function
        # NOTE: cart ko quantity kati xa tesko anusar cart ma banuna
        for i in cart:
            quantity = cart[i]['quantity']
            createUpdateOrder(request, i, '', quantity)

    # END OF COOKIES

    context = {"cartItems": cartItems, "categories": categories, "products": products, "orderItems": orderItems,
               "recom_searched_products": recom_searched_products, "recom_viewed_products": recom_viewed_products, "most_viewed_products": most_viewed_products, "orderItem_name_quantity_2D": orderItem_name_quantity_2D}
    return render(request, "store/store.html", context)


# category wise products
def categoryProducts(request, slug):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.filter(category__slug=slug, disable=False)

    # PAGINATION
    paginator = Paginator(products, 4)  # Shows 4 products per page.
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {"products": products, "cartItems": cartItems, }
    return render(request, "store/categoryProducts.html", context)

# Customer Profile


def customerProfile(request):
    data = cartData(request)
    cartItems = data['cartItems']

    customer = request.user.customer
    # orders expect the order_status="Order Canceled"
    # orders=Order.objects.filter(customer=customer, complete=True,).exclude(order_status="Order Canceled").order_by("-id")
    orderItems = OrderItem.objects.filter(order__customer=customer).exclude(
        orderItem_order_status="Order Canceled").order_by("-id")
    context = {"customer": customer,
               "orderItems": orderItems, "cartItems": cartItems, }
    return render(request, "store/customerProfile.html", context)


# Customer Order Detail
def customerOrderDetail(request, pk):
    data = cartData(request)
    cartItems = data['cartItems']

    order = Order.objects.filter(id=pk)
    shippingAddress = ShippingAddress.objects.filter(order_id=pk)
    orderItems = OrderItem.objects.filter(order_id=pk)
    context = {"cartItems": cartItems, "order": order,
               "shippingAddress": shippingAddress, "orderItems": orderItems}
    return render(request, "store/customerOrderDetail.html", context)

# cancel the order with the click of the button


def cancelOrder(request, pk):
    orderItems = OrderItem.objects.filter(id=pk)
    for orderItem in orderItems:
        orderItem.orderItem_order_status = "Order Canceled"
        orderItem.noti_status = True
        orderItem.save()
    return redirect(reverse_lazy("app:customer-profile"))

# SELLER


class sellerRegister(CreateView):
    template_name = "store/seller/sellerRegister.html"
    form_class = sellerRegisterForm
    success_url = reverse_lazy("app:seller-login")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        messages.success(self.request, "Account was created for ", uname)

        user = User.objects.create_user(
            form.cleaned_data.get("username"),
            email=form.cleaned_data.get("email"),
            password=form.cleaned_data.get("password1"),
        )

        form.instance.user = user

        return super().form_valid(form)


def sellerLogin(request):

    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None and Seller.objects.filter(user__username=username).exists():
            login(request, user)
            return redirect("app:seller-home")
        else:
            messages.info(request, "Username OR Password is incorrect")

    return render(request, "store/seller/sellerLogin.html", {})


def sellerLogout(request):
    logout(request)
    return redirect("app:store")


# Will allows the login user and seller to use the views
class SellerRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated() and Seller.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/sellerLogin/")
        return super().dispatch(request, *args, **kwargs)


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

    # BAR-CHART (Total Income)

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

    # x and y component
    x = orderItem_name
    y = orderItem_total_price

    # Bar chart colors
    colors = ['limegreen', 'pink'] * len(orderItem_name)

    # Create a trace json to hold graph data
    trace = {
        'x': x,
        'y': y,
        'type': 'bar',
        'name': x,
        'marker': {'color': colors}
    }

    # Configure the chart's layout
    layout = {'title': {'text': 'Total Income',
                        'font': {
                                'color': '#ffffff'}
                        },
              'xaxis': {'title': "Product's Name", 'color': '#DCDCDC', 'mirror': 'true', 'showline': 'false'},
              'yaxis': {'title': 'Total Price ($)', 'color': '#DCDCDC', 'mirror': 'true', 'showline': 'true'},
              'plot_bgcolor': '#38393d', 'paper_bgcolor': '#38393d', 'bordercolor': '#ffffff'}

    context = {"orders": orders, "seller": seller,
               'orderItemQuantity': orderItemQuantity, 'totalPrice': totalPrice, "trace": trace,
               "layout": layout, "title": "Total Income"}

    return render(request, "store/seller/sellerHome.html", context)


# No of views of a product
def viewsInProductGraph(request):
    seller = request.user.seller

    # BAR-CHART (No of Views)

    # creating a list of all product names with its view_count
    all_product_names = []
    all_product_counts = []

    product_names = Product.objects.filter(seller=seller)

    for product in product_names:
        all_product_names.append(product.name)
        all_product_counts.append(product.view_count)

    # x and y component
    x = all_product_names
    y = all_product_counts

    # Bar chart colors
    colors = ['limegreen', 'pink'] * len(all_product_names)

    # Create a trace json to hold graph data
    trace = {
        'x': x,
        'y': y,
        'type': 'bar',
        'name': x,
        'marker': {'color': colors}
    }

    # Configure the chart's layout
    layout = {'title': {'text': 'Number of views in a Product',
                        'font': {
                            'color': '#ffffff'}
                        },
              'xaxis': {'title': "Product's Name", 'color': '#DCDCDC', 'mirror': 'true', 'showline': 'false'},
              'yaxis': {'title': 'View Count', 'color': '#DCDCDC', 'mirror': 'true', 'showline': 'true'},
              'plot_bgcolor': '#38393d', 'paper_bgcolor': '#38393d', 'bordercolor': '#ffffff'}

    # END OF BAR-CHART (No of Views)

    context = {"trace": trace, "layout": layout,
               "title": "Number of views in a Product"}

    return render(request, "store/seller/viewsInProductGraph.html", context=context)


# Total quantity sold for an product
def quantityProductGraph(request):
    seller = request.user.seller

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

    # Main Scatter Plot section

    # color
    colors = ['limegreen', ] * len(orderItem_name)

    # Create a trace json to hold graph data
    trace = {
        'x': orderItem_name,
        'y': orderItem_total_quantity,
        'type': 'scatter',
        'marker': {'color': colors},
    }

    # Configure the chart's layout
    layout = {'title': {'text': 'Total Quantity Sold',
                        'font': {
                            'color': '#ffffff'}
                        },
              'xaxis': {'title': "Product's Name", 'color': '#DCDCDC', 'mirror': 'true', 'showline': 'false'},
              'yaxis': {'title': 'Quantity', 'color': '#DCDCDC', 'mirror': 'true', 'showline': 'true'},
              'plot_bgcolor': '#38393d', 'paper_bgcolor': '#38393d', 'bordercolor': '#ffffff'}

    # Pass trace and layout in the context
    context = {"trace": trace, "layout": layout,
               "title": "Total Quantity Sold"}

    return render(request, "store/seller/quantityProductGraph.html", context=context)


def sellerProfile(request):
    seller = request.user.seller

    context = {'seller': seller, }
    return render(request, "store/seller/sellerProfile.html", context)


# class sellerProfileUpdate(UpdateView):
#     template_name = "store/seller/sellerProfileUpdate.html"
#     queryset = Seller.objects.all()
#     form_class = SellerProfileUpdateForm

#     def get_success_url(self):
#         return reverse_lazy("app:seller-profile")

def sellerProfileUpdate(request, pk):
    seller = request.user.seller
    form = SellerProfileUpdateForm(instance=seller)
    if request.method == 'POST':
        form = SellerProfileUpdateForm(request.POST, instance=seller)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy("app:seller-profile"))

    context = {
        "seller": seller,
        "form": form
    }
    return render(request, "store/seller/sellerProfileUpdate.html", context)


class sellerOrderDetail(DetailView):
    template_name = "store/seller/sellerOrderDetail.html"

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
    context = {"allorders": allorders}
    return render(request, "store/seller/sellerOrderList.html", context)


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
    return render(request, "store/seller/sellerProductList.html", context)


class sellerProductAdd(CreateView):
    template_name = "store/seller/sellerProductAdd.html"
    form_class = ProductForm
    success_url = reverse_lazy("app:seller-product-list")

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
        # order_obj = Order.objects.get(id=order_id)

        new_status = request.POST.get("status")
        # order_obj.order_status = new_status
        # order_obj.save()

        orderItem_obj = OrderItem.objects.filter(
            order__id=order_id, product__seller=seller)

        for orderItem in orderItem_obj:
            if orderItem.orderItem_order_status == "Order Canceled":
                orderItem.orderItem_order_status == "Order Canceled"
                orderItem.save()
            else:
                orderItem.orderItem_order_status = new_status
                orderItem.save()
        return redirect(reverse_lazy("app:seller-order-detail", kwargs={"pk": order_id}))


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
    return render(request, "store/seller/sellerProductDetail.html", context)


class sellerProductUpdate(UpdateView):
    template_name = 'store/seller/sellerProductUpdate.html'
    queryset = Product.objects.all()
    form_class = ProductForm

    def get_success_url(self):
        return reverse_lazy("app:seller-product-detail", args=[self.kwargs['slug']])


def productDelete(request, pk):
    product = Product.objects.get(id=pk)
    product.delete()
    return redirect(reverse_lazy("app:seller-product-list"))


def productDisable(request, slug):
    product = Product.objects.get(slug=slug)
    product.disable = True
    product.save()
    return redirect(reverse_lazy("app:seller-product-detail", args=[slug]))


def productEnable(request, slug):
    product = Product.objects.get(slug=slug)
    product.disable = False
    product.save()
    return redirect(reverse_lazy("app:seller-product-detail", args=[slug]))


# End Of SELLER


# @login_required(login_url='app:customer-login')
def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {"items": items, "order": order, "cartItems": cartItems, }
    return render(request, "store/cart.html", context)


@login_required(login_url='app:customer-registration')
def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {"items": items, "order": order, "cartItems": cartItems, }
    return render(request, "store/checkout.html", context)


# click in the item and see its details
def productDetail(request, slug):
    data = cartData(request)
    cartItems = data['cartItems']

    # Increasing the view_count of respective product after each visit
    product = Product.objects.get(slug=slug)
    product.view_count += 1
    product.save()

    # DISCOUNT
    discountPrice = 0
    if product.discount > 0.0:
        discountPrice = decimal.Decimal(product.price) - \
            (((decimal.Decimal(product.discount))/decimal.Decimal(100))
             * decimal.Decimal(product.price))

    # RECOMENDATION
    if request.user.is_authenticated:
        customer = request.user.customer

        # Adding the viewed Product name to the database
        recommend, created = Recommendation.objects.get_or_create(
            customer=customer)
        recommend.view_product = product.name
        recommend.save()

    # Comment AND reply
    comments = ProductComment.objects.filter(
        product=product, parent=None).order_by("-sno")
    replies = ProductComment.objects.filter(
        product=product).exclude(parent=None)

    context = {"product": product,
               "cartItems": cartItems, "discountPrice": discountPrice, "comments": comments, "replies": replies, }
    return render(request, "store/productDetail.html", context)


def postComment(request):
    if request.method == 'POST':
        comment = request.POST.get("comment")
        user = request.user
        productId = request.POST.get("productId")
        product = Product.objects.get(id=productId)
        parentSno = request.POST.get("parentSno")

        if parentSno == "":
            comment = ProductComment.objects.create(
                comment=comment, user=user, product=product)
            comment.save()
        else:
            parent = ProductComment.objects.get(sno=parentSno)
            comment = ProductComment.objects.create(
                comment=comment, user=user, product=product, parent=parent)
            comment.save()

    if Seller.objects.filter(user__username=user.username):
        return redirect(f"/seller-product-detail/{product.slug}/")
    elif Customer.objects.filter(user__username=user.username):
        return redirect(f"/product-detail/{product.slug}/")


# search items from its name
def searchItems(request):
    data = cartData(request)
    cartItems = data['cartItems']

    # getting the searched value
    searchProduct = request.GET['search']

    # NOTE:RECOMMENDATION
    if request.user.is_authenticated:
        customer = request.user.customer

        # Adding the searched Product name to the database
        recommend, created = Recommendation.objects.get_or_create(
            customer=customer)
        recommend.search_product = searchProduct
        recommend.save()

    # NOTE:SORT_BY of the searched Products
    filter_by = ""
    if request.method == 'POST':
        form = FilterForm(request.POST or None)
        if form.is_valid():
            filter_by = form.cleaned_data.get('filter_by')
            # filter_by = request.POST.get('filter_by')

    # main SEARCH functionality
    # "__icontains" will allows to search for the similiar content. Order by price (max-min)
    if filter_by == "PriceHighToLow":
        products = Product.objects.filter(Q(name__icontains=searchProduct) | Q(
            description__icontains=searchProduct) | Q(category__title__icontains=searchProduct), disable=False).order_by('-price')

    elif filter_by == "PriceLowToHigh":
        products = Product.objects.filter(Q(name__icontains=searchProduct) | Q(
            description__icontains=searchProduct) | Q(category__title__icontains=searchProduct), disable=False).order_by('price')

    elif filter_by == "mostPopular":
        products = Product.objects.filter(Q(name__icontains=searchProduct) | Q(
            description__icontains=searchProduct) | Q(category__title__icontains=searchProduct), disable=False).order_by('-view_count')

    elif filter_by == "newestArrivals":
        products = Product.objects.filter(Q(name__icontains=searchProduct) | Q(
            description__icontains=searchProduct) | Q(category__title__icontains=searchProduct), disable=False).order_by('-date_added')

    else:
        products = Product.objects.filter(Q(name__icontains=searchProduct) | Q(
            description__icontains=searchProduct) | Q(category__title__icontains=searchProduct), disable=False)

    # DISCOUNT
    discountPrice = 0.0
    for product in products:
        if product.discount > 0.0:
            discountPrice = decimal.Decimal(product.price) - \
                ((decimal.Decimal(product.discount)/decimal.Decimal(100))
                 * decimal.Decimal(product.price))
        else:
            discountPrice = 0.0

    context = {"products": products, "cartItems": cartItems,
               "discountPrice": discountPrice, }
    return render(request, "store/search.html", context)


# making this function so that we dont have to repeat again
def createUpdateOrder(request, productId, action, quantity=0):
    customer = request.user.customer
    product = Product.objects.get(id=productId, disable=False)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    # for cookies OrderItems
    if quantity != 0:

        # yo garna milxa hola
        # if OrderItem.objects.filter(product__id=productId, order__id=order.id).exists():
        #     pass

        if product.quantity >= quantity:
            orderItem, created = OrderItem.objects.get_or_create(
                order=order, product=product, quantity=quantity)

        # if the orderItem send from the guest user, qunatity is greater then actual product quantity
        else:
            orderItem, created = OrderItem.objects.get_or_create(
                order=order, product=product, quantity=product.quantity)

    # for those items added from the user in site
    else:
        orderItem, created = OrderItem.objects.get_or_create(
            order=order, product=product)

    if action == 'add':
        if orderItem.quantity >= product.quantity:
            orderItem.quantity = orderItem.quantity

        else:
            orderItem.quantity = (orderItem.quantity + 1)

    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()


# to send the add to cart data to the backend
def updateItem(request):
    # parse the data and is stored as python dictionary
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    createUpdateOrder(request, productId, action)

    return JsonResponse('Data was added', safe=False)


# to send shipping info to the backend
def processOrder(request):
    # using time stamp as the transaction_id
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    customer = request.user.customer
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    # to check if the total price we send is equal to the actual total
    # if total == order.totalCartPrice:
    order.complete = True
    order.save()

    # we need to save these values to the database or to create an instance of shipping address
    ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],
    )

    # DECREASE the product quanity after each purchase
    name_array = data['productNameArray']
    quanity_array = data['productQuantityArray']

    for i in range(len(name_array)):
        product = Product.objects.get(name=name_array[i])
        product.quantity = product.quantity - int(quanity_array[i])
        product.save()

    return JsonResponse('Payment submitted....', safe=False)
    # maybe add orderItems to the ShippingAddress
