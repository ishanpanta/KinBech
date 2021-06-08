from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [

    # CUSTOMER
    path('customerRegister/', views.CustomerRegistrationView.as_view(),
         name="customer-registration"),
    path('customerLogin/', views.customerLogin, name="customer-login"),
    path('customerLogout/', views.customerLogout, name="customer-logout"),

    # SELLER
    path('sellerRegister/', views.sellerRegister.as_view(), name="seller-register"),
    path('sellerLogin/', views.sellerLogin, name="seller-login"),
    path('sellerLogout/', views.sellerLogout, name="seller-logout"),
]
