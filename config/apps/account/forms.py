from django import forms

from .models import User, CustomerProfile, Address


class UserAccountForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "phone_number",
        ]

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام کاربری",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "ایمیل",
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "09123456789",
                    "maxlength": "11",
                }
            ),
        }


class CustomerProfileForm(forms.ModelForm):

    class Meta:
        model = CustomerProfile

        fields = [
            "first_name",
            "last_name",
            "national_code",
            "avatar",
        ]

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام خانوادگی",
                }
            ),

            "national_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "کد ملی ۱۰ رقمی",
                    "maxlength": "10",
                }
            ),

            "avatar": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }




class AddressForm(forms.ModelForm):


    class Meta:

        model = Address


        fields = [
            "title",
            "receiver_name",
            "phone_number",
            "province",
            "city",
            "address",
            "postal_code",
        ]


        labels = {

            "title": "عنوان آدرس",

            "receiver_name": "نام و نام خانوادگی گیرنده",

            "phone_number": "شماره موبایل گیرنده",

            "province": "استان",

            "city": "شهر",

            "address": "آدرس کامل",

            "postal_code": "کد پستی",

        }


        widgets = {

            "title": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً خانه، محل کار، منزل والدین",
                }
            ),


            "receiver_name": forms.TextInput(
                attrs={
                    "placeholder": "نام و نام خانوادگی گیرنده",
                }
            ),


            "phone_number": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً 09123456789",
                    "inputmode": "numeric",
                    "maxlength": "11",
                }
            ),


            "province": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً تهران",
                }
            ),


            "city": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً تهران",
                }
            ),


            "address": forms.Textarea(
                attrs={
                    "placeholder": "آدرس کامل شامل خیابان، کوچه، پلاک و واحد",
                    "rows": 4,
                }
            ),


            "postal_code": forms.TextInput(
                attrs={
                    "placeholder": "کد پستی ۱۰ رقمی",
                    "inputmode": "numeric",
                    "maxlength": "10",
                }
            ),

        }