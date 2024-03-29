from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy

from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from ecommerce.settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import *
from .forms import *
from .utils import cartData

from operator import itemgetter
import datetime
import decimal
import json


# CUSTOMER and GUEST USER
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
        # 'i' means the productID
        for i in cart:
            quantity = cart[i]['quantity']
            createUpdateOrder(request, i, '', quantity)

    # END OF COOKIES

    context = {"cartItems": cartItems, "categories": categories, "products": products, "orderItems": orderItems,
               "recom_searched_products": recom_searched_products, "recom_viewed_products": recom_viewed_products, "most_viewed_products": most_viewed_products, "orderItem_name_quantity_2D": orderItem_name_quantity_2D}
    return render(request, "store/store.html", context)


# CUSTOMER and GUEST USER
# category wise products
def categoryProducts(request, slug):
    data = cartData(request)

    cartItems = data['cartItems']

    products = Product.objects.filter(
        category__slug=slug, disable=False).order_by("id")

    # PAGINATION
    paginator = Paginator(products, 4)  # Shows 4 products per page.
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {"products": products, "cartItems": cartItems, }
    return render(request, "store/categoryProducts.html", context)


# CUSTOMER
# Customer Profile
def customerProfile(request):
    data = cartData(request)
    cartItems = data['cartItems']

    customer = request.user.customer

    # orders expect the order_status="Order Canceled"
    # orders=Order.objects.filter(customer=customer, complete=True,).exclude(order_status="Order Canceled").order_by("-id")
    orderItems = OrderItem.objects.filter(order__customer=customer, order__complete=True).exclude(
        orderItem_order_status="Order Canceled").order_by("-id")
    context = {"customer": customer,
               "orderItems": orderItems, "cartItems": cartItems, }
    return render(request, "store/customerProfile.html", context)


# CUSTOMER
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


# CUSTOMER and SELLER
def postComment(request):
    if request.method == 'POST':
        comment = request.POST.get("comment")
        user = request.user
        productId = request.POST.get("productId")
        product = Product.objects.get(id=productId)
        parentSno = request.POST.get("parentSno")

        # this is the comment
        if parentSno == "":
            comment = ProductComment.objects.create(
                comment=comment, user=user, product=product)
            comment.save()

        # this is the reply
        else:
            parent = ProductComment.objects.get(sno=parentSno)
            comment = ProductComment.objects.create(
                comment=comment, user=user, product=product, parent=parent)
            comment.save()

    # if seller is posting the comment then redirect to this path
    if Seller.objects.filter(user__username=user.username):
        return redirect(f"../seller/seller-product-detail/{product.slug}/")

    # if customer is posting the comment then redirect to this path
    elif Customer.objects.filter(user__username=user.username):
        return redirect(f"/product-detail/{product.slug}/")


# CUSTOMER
# cancel the order with the click of the button
def cancelOrder(request, pk):
    orderItems = OrderItem.objects.filter(id=pk)

    for orderItem in orderItems:
        orderItem.orderItem_order_status = "Order Canceled"
        orderItem.noti_status = True
        orderItem.save()
    return redirect(reverse_lazy("app:customer-profile"))


# CUSTOMER and GUEST USER
# @login_required(login_url='app:customer-login')
def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {"items": items, "order": order, "cartItems": cartItems, }
    return render(request, "store/cart.html", context)


# CUSTOMER
@login_required(login_url='auth:customer-registration')
def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {"items": items, "order": order, "cartItems": cartItems, }
    return render(request, "store/checkout.html", context)


# CUSTOMER and GUEST USER
# click in the item and see its details
def productDetail(request, slug):
    data = cartData(request)
    cartItems = data['cartItems']

    # Increasing the view_count of respective product after each visit
    product = Product.objects.get(slug=slug)
    product.view_count += 1
    product.save()

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

    context = {"product": product, "cartItems": cartItems,
               "comments": comments, "replies": replies, }
    return render(request, "store/productDetail.html", context)


# CUSTOMER and GUEST USER
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

    # NOTE: ALL BRAND NAMES

    # list containing all the brand names
    brand_name_of_all_product_list = []

    # appending brand names of all products
    # DIsplaying the brand names
    for product in Product.objects.all():
        brand_name_of_all_product_list.append(product.brand)

    # END OF ALL BRAND NAMES

    # NOTE: BRAND WISE AND PRICE RANGE SEARCH

    # initilizing the brand_name to None and price_range to 0
    brand_select_price_range_list = [None, 0]

    # initilizing the price_range_list to 0
    split_price_range_list = ['0', '0']

    # if user chooses brand_name only then it's status will be changed
    price_range = True

    # geting the list of the choosed brand name and price range. (i.e.['brand_name', 'price_range'])
    if request.method == "POST":
        brand_select_price_range_list = request.POST.getlist(
            'price_range_brand_select')

        try:
            price_list = []

            # appending the price_range to the list so that it can iterable as required
            price_list.append(brand_select_price_range_list[1])

            # spliting the price_range to the two part. So it could be passed in queryset.
            for price in price_list:

                # replacing first-'0' of the list with the first three number of price range
                split_price_range_list[0] = price[0:3]

                # replacing second-'0' of the list with the remaining numbers
                split_price_range_list[1] = price[3:len(price)]

        except:

            # if user chooses brand_name only then status of price_range will be changed
            try:
                if brand_select_price_range_list[0] in brand_name_of_all_product_list:
                    price_range = False
            except:
                pass

    try:

        # if user chooses brand_name only then products of that brand_name will be displayed
        if price_range == False:
            products = Product.objects.filter(
                brand=brand_select_price_range_list[0])

        # run only if any brand name is chooosed
        # Displaying the products acording to the choosed brand
        if brand_select_price_range_list[0] != None and brand_select_price_range_list[1] != 0 and split_price_range_list[0] != '0' and split_price_range_list[1] != '0':

            products = Product.objects.filter(brand=brand_select_price_range_list[0], price__range=(
                int(split_price_range_list[0]), int(split_price_range_list[1])))    # price_range = (min,max)
    except:
        pass

    # END OF BRAND WISE AND PRICE RANGE SEARCH

    try:
        context = {"products": products, "cartItems": cartItems,
                   "brand_name_of_all_product_list": list(set(brand_name_of_all_product_list)), "price_range_status": price_range, "first_price_range": int(split_price_range_list[0]), "second_price_range": int(split_price_range_list[1])}
    except:
        context = {"products": products, "cartItems": cartItems,
                   "brand_name_of_all_product_list": list(set(brand_name_of_all_product_list)), "price_range_status": price_range, "flag": True, }

    return render(request, "store/search.html", context)


# CUSTOMER and GUEST USER
# making this function so that we dont have to repeat again
def createUpdateOrder(request, productId, action, quantity=0):
    customer = request.user.customer
    product = Product.objects.get(id=productId, disable=False)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    # for cookies OrderItems
    # Guest user
    if quantity != 0:

        # if orderItem from the cookie already exits iin the  customer cart then new orderItem willnot
        # be created instead the quantity will be added to the pre-exiting orderItem present in the cart.
        try:

            # get orderItem with the which has the present orderId and productID
            orderItem = OrderItem.objects.get(
                order__id=order.id, product__id=product.id)

            # adding quantity to the pre-exiting orderItem instead of creating new orderItem in cart
            if product.quantity >= orderItem.quantity:
                orderItem.quantity += quantity

                # total gare paxi feri check garne
                # now check if orderItem quantity is greater than product actual quantity
                if orderItem.quantity > product.quantity:
                    orderItem.quantity = product.quantity
            else:
                orderItem.quantity = product.quantity

            orderItem.save()

        # if cookie orderItem doesnot exists in the customer cart
        except:
            if product.quantity >= quantity:
                orderItem, created = OrderItem.objects.get_or_create(
                    order=order, product=product, quantity=quantity)

            # if the orderItem qunatity send from the guest user is greater then actual product quantity
            else:
                orderItem, created = OrderItem.objects.get_or_create(
                    order=order, product=product, quantity=product.quantity)

    # Login User
    else:
        orderItem, created = OrderItem.objects.get_or_create(
            order=order, product=product)

    if action == 'add':
        # orderItem quantity cannot be greater than defined (database) quantity
        if orderItem.quantity >= product.quantity:
            orderItem.quantity = orderItem.quantity

        else:
            orderItem.quantity = (orderItem.quantity + 1)

    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()


# CUSTOMER and GUEST USER
# to access the add_to_cart data sent from frontend to backend
def updateItem(request):
    # parse the data and is stored as python dictionary
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    createUpdateOrder(request, productId, action)

    return JsonResponse('Data was added', safe=False)


# CUSTOMER and GUEST USER
# to access the shipping info sent from frontend to backend
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
    shippingAddress = ShippingAddress.objects.create(
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

    # OrderItems of the order
    orderItems = OrderItem.objects.filter(order__id=order.id)

    # NOTE SENDING EMAIL TO THE SELLER AFTER CUSTOMER buys some products
    subject = "New Order by " + order.customer.user.username

    html_message = render_to_string("store/emailMessage.html", {
                                    'shippingAddress': shippingAddress, 'orderItem_obj': orderItems, 'order_obj': order, })

    message = strip_tags(html_message)

    # empty list of recepient email
    recepient = []

    for oi in orderItems:
        seller_email = oi.product.seller.user.email
        recepient.append(seller_email)

    email = EmailMultiAlternatives(
        subject,
        message,
        EMAIL_HOST_USER,

        # no repeat of same email
        list(set(recepient)),
    )

    email.attach_alternative(html_message, "text/html")
    email.send()
    # End of emails

    return JsonResponse('Payment submitted....', safe=False)
