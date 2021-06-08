from django.urls import path
from . import views

app_name = "seller"

urlpatterns = [

    # SELLER
    path('sellerHome/', views.sellerHome, name="seller-home"),


    # Seller ORder
    # detail
    path('seller-order-detail/<int:pk>/',
         views.sellerOrderDetail.as_view(), name="seller-order-detail"),

    # list
    path('seller-order-list/', views.sellerOrderList, name="seller-order-list"),

    # Status-change
    path('seller-order-<int:pk>-change/',
         views.sellerOrderStatusChange.as_view(), name="seller-order-status-change"),
    # END OF Seller ORder


    # Seller Product
    # list
    path('seller-product/list/', views.sellerProductList,
         name="seller-product-list"),

    # add
    path('seller-product/add/', views.sellerProductAdd.as_view(),
         name="seller-product-add"),

    # detail
    path('seller-product-detail/<slug:slug>/',
         views.sellerProductDetail, name="seller-product-detail"),

    # update
    path('seller-product-update/<slug:slug>',
         views.sellerProductUpdate.as_view(), name="seller-product-update"),
    # END OF Seller Product


    # Seller Profile
    # profile
    path('seller-profile/', views.sellerProfile, name="seller-profile"),

    # update
    path('seller-profile-update/<int:pk>', views.sellerProfileUpdate,
         name="seller-profile-update"),
    # END OF Seller Profile


    # PRODUCT - delete, disable, enable
    path('product-delete/<int:pk>', views.productDelete, name="product-delete"),
    path('product-disable/<slug:slug>',
         views.productDisable, name="product-disable"),
    path('product-enable/<slug:slug>',
         views.productEnable, name="product-enable"),
]
