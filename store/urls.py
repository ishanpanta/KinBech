from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),


    path('product-detail/<slug:slug>/',
         views.productDetail, name="productDetail"),
    path('search/', views.searchItems, name="search"),
    path('category/<slug:slug>/', views.categoryProducts, name="category-products"),


    # CUSTOMER
    path('customer-profile/', views.customerProfile, name="customer-profile"),
    path('customer-order-detail/<int:pk>',
         views.customerOrderDetail, name="customer-order-detail"),
    path('cancel-order/<int:pk>', views.cancelOrder, name="cancel-order"),

    path('postComment/', views.postComment, name="postcomment"),


    # fetch api urls paths
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order")
]
