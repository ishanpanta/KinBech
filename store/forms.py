# convert the exciting model into the form
from django import forms
from django.contrib.auth.models import User
from .models import *
import re

# pattern to exclude @,$ and other special characters
username_pattern = "^[A-Za-z0-9_-]*$"
phone_pattern = "^[ 0-9+-]*$"
name_pattern = "^[ A-Za-z]*$"

# we are using CreateView so we need ModelForm


class customerRegistrationForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput())
    username = forms.CharField(widget=forms.TextInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(widget=forms.EmailInput())
    phone = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = Customer
        fields = ("name", "username", "email",
                  "password1", "password2", "phone")

    def clean_username(self):
        uname = self.cleaned_data.get("username")

        # convert match object into boolean values
        userName = bool(re.match(username_pattern, uname))

        if userName == False:
            raise forms.ValidationError("Username should not contain @,$,%.")

        # checks if there is another user with the same username
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError("Username already exists.")
        return uname

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        phone_number = bool(re.match(phone_pattern, phone))

        if phone_number == False:
            raise forms.ValidationError(
                "Contact Number should not contain A-Za-z@#$.")

        return phone

    def clean_name(self):
        name = self.cleaned_data.get("name")

        fullName = bool(re.match(name_pattern, name))

        if fullName == False:
            raise forms.ValidationError("Name should not contain A-Za-z.")

        return name

    def clean_password2(self):
        pword = self.cleaned_data.get("password1")
        re_pword = self.cleaned_data.get("password2")

        # checks if the password and re_password is same or not
        if pword and re_pword and pword != re_pword:
            raise forms.ValidationError("Password don't match")
        return re_pword


class sellerRegisterForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput())
    username = forms.CharField(widget=forms.TextInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(widget=forms.EmailInput())
    phone = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = Seller
        fields = ("name", "username", "email",
                  "password1", "password2", "phone")

    def clean_username(self):
        uname = self.cleaned_data.get("username")

        # convert match object into boolean values
        userName = bool(re.match(username_pattern, uname))

        if userName == False:
            raise forms.ValidationError("Username should not contain @,$,%.")

        # checks if there is another user with the same username
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError("Username already exists.")
        return uname

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        phone_number = bool(re.match(phone_pattern, phone))

        if phone_number == False:
            raise forms.ValidationError(
                "Contact Number should not contain A-Za-z@#$.")

        return phone

    def clean_name(self):
        name = self.cleaned_data.get("name")

        fullName = bool(re.match(name_pattern, name))

        if fullName == False:
            raise forms.ValidationError("Name should not contain A-Za-z.")

        return name

    def clean_password2(self):
        pword = self.cleaned_data.get("password1")
        re_pword = self.cleaned_data.get("password2")

        # checks if the password and re_password is same or not
        if pword and re_pword and pword != re_pword:
            raise forms.ValidationError("Password don't match")
        return re_pword


# add new product
# NOTE: all the fields that are from the meta class are saved automatically but the custom
# fields are not saved automatically. To save this we have to save exciptly from the views.

class ProductForm(forms.ModelForm):
    # custom field in the form
    more_images = forms.FileField(required=False, widget=forms.FileInput(attrs={
        "class": "form-control",
        "multiple": True,
    }))

    class Meta:
        model = Product
        fields = ["name", "slug", "price", "quantity", "discount", "category", "image",
                  "description", "warranty", "return_policy"]

        # to contumize our form fields, widgets is defined
        widgets = {
            "name": forms.TextInput(attrs={
                # form-control class is a bootstrap class which will make our form responsive
                "class": "form-control",
                "placeholder": "Enter the product name here..."
            }),

            "slug": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the unique slug here..."
            }),

            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Price of the product..."
            }),

            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Quantity of the product..."
            }),

            "discount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Discount of the product..."
            }),

            "category": forms.Select(attrs={
                "class": "form-control",
            }),

            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Description of the product...",
                "rows": 5
            }),

            "warranty": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the product warranty here..."
            }),

            "return_policy": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the product return policy here..."
            }),
        }


# Filter By
class FilterForm(forms.Form):
    FILTER_CHOICES = (
        ('PriceHighToLow', 'Price: High To Low'),
        ('PriceLowToHigh', 'Price: Low To High'),
        ('mostPopular', 'Most Popular'),
        ('newestArrivals', 'Newest Arrivals')
    )

    filter_by = forms.ChoiceField(choices=FILTER_CHOICES)


# Seller Profile Update Form
class SellerProfileUpdateForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Conform Password..."
        })
    )

    email = forms.CharField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Email..."
        })
    )

    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )

    class Meta:
        model = Seller
        fields = (
            "name", "username", "email",
            "password1", "password2", "phone", "image"
        )

    def clean_username(self):
        uname = self.cleaned_data.get("username")

        # convert match object into boolean values
        userName = bool(re.match(username_pattern, uname))

        if userName == False:
            raise forms.ValidationError("Username should not contain @,$,%.")

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        phone_number = bool(re.match(phone_pattern, phone))

        if phone_number == False:
            raise forms.ValidationError(
                "Contact Number should not contain A-Za-z@#$.")

        return phone

    def clean_name(self):
        name = self.cleaned_data.get("name")

        fullName = bool(re.match(name_pattern, name))

        if fullName == False:
            raise forms.ValidationError("Name should only contain A-Za-z.")

        return name

    def clean_password2(self):
        pword = self.cleaned_data.get("password1")
        re_pword = self.cleaned_data.get("password2")

        # checks if the password and re_password is same or not
        if pword and re_pword and pword != re_pword:
            raise forms.ValidationError("Password don't match")
        return re_pword
