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
    path('register/', views.CustomerRegistrationView.as_view(),
         name="customer-registration"),
    path('login/', views.customerLogin, name="customer-login"),
    path('logout/', views.customerLogout, name="customer-logout"),

    path('customer-profile/', views.customerProfile, name="customer-profile"),
    path('customer-order-detail/<int:pk>',
         views.customerOrderDetail, name="customer-order-detail"),
    path('cancel-order/<int:pk>', views.cancelOrder, name="cancel-order"),
    path('postComment/', views.postComment, name="postcomment"),


    # SELLER
    path('sellerRegister/', views.sellerRegister.as_view(), name="seller-register"),
    path('sellerLogin/', views.sellerLogin, name="seller-login"),
    path('sellerLogout/', views.sellerLogout, name="seller-logout"),

    path('sellerHome/', views.sellerHome, name="seller-home"),


    path('seller-order-detail/<int:pk>/',
         views.sellerOrderDetail.as_view(), name="seller-order-detail"),
    path('seller-order-list/', views.sellerOrderList, name="seller-order-list"),

    path('seller-order-<int:pk>-change/',
         views.sellerOrderStatusChange.as_view(), name="seller-order-status-change"),
    path('seller-product/list/', views.sellerProductList,
         name="seller-product-list"),

    path('seller-product/add/', views.sellerProductAdd.as_view(),
         name="seller-product-add"),
    path('seller-product-detail/<slug:slug>/',
         views.sellerProductDetail, name="seller-product-detail"),
    path('seller-profile/', views.sellerProfile, name="seller-profile"),

    path('seller-profile-update/<int:pk>', views.sellerProfileUpdate,
         name="seller-profile-update"),
    path('seller-product-update/<slug:slug>',
         views.sellerProductUpdate.as_view(), name="seller-product-update"),
    path('product-delete/<int:pk>', views.productDelete, name="product-delete"),

    path('product-disable/<slug:slug>',
         views.productDisable, name="product-disable"),
    path('product-enable/<slug:slug>',
         views.productEnable, name="product-enable"),


    # fetch api urls paths
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order")
]
