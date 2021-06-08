from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.contrib.auth import authenticate, login, logout
from django.views.generic import CreateView
from django.contrib import messages

from store.models import *
from store.forms import *

# CUSTOMER
# Registration


class CustomerRegistrationView(CreateView):
    template_name = "authentication/customerRegistration.html"
    form_class = customerRegistrationForm
    success_url = reverse_lazy("auth:customer-login")

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

    return render(request, "authentication/customerLogin.html", {})


# Logout
def customerLogout(request):
    logout(request)
    return redirect("app:store")

# END OF CUSTOMER


# SELLER
# Registration
class sellerRegister(CreateView):
    template_name = "authentication/sellerRegister.html"
    form_class = sellerRegisterForm
    success_url = reverse_lazy("auth:seller-login")

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
            return redirect("seller:seller-home")
        else:
            messages.info(request, "Username OR Password is incorrect")

    return render(request, "authentication/sellerLogin.html", {})


def sellerLogout(request):
    logout(request)
    return redirect("app:store")

# END OF SELLER
