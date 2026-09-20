from django import forms
from django.forms import inlineformset_factory
from django_ckeditor_5.widgets import CKEditor5Widget
from apps.shop.models import (
    Product,
    ProductVariant,
    Category,
    Brand,
    Color,
)





class AdminTokenApprovalForm(forms.Form):

    token = forms.CharField(
        label="کد دسترسی مدیریت",
        max_length=128,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "off",
                "placeholder": "توکن مدیریت"
            }
        ),
    )







# ==========================
# Product Form
# ==========================


class ProductForm(forms.ModelForm):


    class Meta:


        model = Product


        fields = [

            "category",
            "brand",
            "name",
            "display_name",
            "description",
            "image",
            "is_active",

        ]



        labels = {


            "category": "دسته‌بندی",

            "brand": "برند",

            "name": "نام انگلیسی محصول",

            "display_name": "نام نمایشی محصول",

            "description": "توضیحات محصول",

            "image": "تصویر محصول",

            "is_active": "وضعیت محصول",


        }



        widgets = {


            "category": forms.Select(
                attrs={
                    "class": "form-control select-control"
                }
            ),



            "brand": forms.Select(
                attrs={
                    "class": "form-control select-control"
                }
            ),




            "name": forms.TextInput(
                attrs={

                    "class": "form-control",

                    "placeholder":
                    "نام اصلی محصول"

                }
            ),





            "display_name": forms.TextInput(
                attrs={

                    "class": "form-control",

                    "placeholder":
                    "نامی که مشتری مشاهده می‌کند"

                }
            ),





            "description": CKEditor5Widget(
                attrs={

                    "class": "django_ckeditor_5",

                    "placeholder":
                    "توضیحات کامل محصول"

                },
                config_name="default",
            ),





            "image": forms.FileInput(
                attrs={

                    "class":
                    "form-control file-control"

                }
            ),






            "is_active": forms.CheckboxInput(
                attrs={

                    "class":
                    "form-check-input"

                }
            ),


        }





    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)




        self.fields["category"].queryset = (
            Category.objects
            .filter(
                is_active=True
            )
            .order_by(
                "display_name"
            )
        )



        self.fields["brand"].queryset = (
            Brand.objects
            .filter(
                is_active=True
            )
            .order_by(
                "display_name"
            )
        )









# ==========================
# Product Variant Form
# ==========================



class ProductVariantForm(forms.ModelForm):



    class Meta:


        model = ProductVariant



        fields = [

            "color",
            "size",
            "sku_code",
            "barcode",
            "price",
            "stock",
            "reserved_stock",
            "low_stock_threshold",
            "is_active",

        ]





        labels = {



            "color":
            "رنگ",



            "size":
            "سایز",



            "sku_code":
            "کد SKU",



            "barcode":
            "بارکد",



            "price":
            "قیمت",



            "stock":
            "موجودی",



            "reserved_stock":
            "رزرو شده",



            "low_stock_threshold":
            "حد هشدار",



            "is_active":
            "فعال",


        }






        widgets = {



            "color": forms.Select(

                attrs={
                    "class":
                    "form-control select-control"
                }

            ),





            "size": forms.TextInput(

                attrs={

                    "class":
                    "form-control",

                    "placeholder":
                    "سایز"

                }

            ),





            "sku_code": forms.TextInput(

                attrs={

                    "class":
                    "form-control",
                    "readonly":"readonly"

                }

            ),





            "barcode": forms.TextInput(

                attrs={

                    "class":
                    "form-control",

                    "readonly":"readonly"
                    

                }

            ),






            "price": forms.NumberInput(

                attrs={

                    "class":
                    "form-control",

                    "placeholder":
                    "قیمت"

                }

            ),






            "stock": forms.NumberInput(

                attrs={

                    "class":
                    "form-control"

                }

            ),






            "reserved_stock": forms.NumberInput(

                attrs={

                    "class":
                    "form-control"

                }

            ),






            "low_stock_threshold": forms.NumberInput(

                attrs={

                    "class":
                    "form-control"

                }

            ),






            "is_active": forms.CheckboxInput(

                attrs={

                    "class":
                    "form-check-input"

                }

            ),


        }






    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)



        self.fields["sku_code"].disabled = True

        self.fields["barcode"].disabled = True

        

        self.fields["color"].queryset = (
            Color.objects
            .order_by(
                "display_name"
            )
        )









# ==========================
# Variant FormSet
# ==========================



ProductVariantFormSet = inlineformset_factory(

    Product,

    ProductVariant,

    form=ProductVariantForm,

    extra=0,

    can_delete=True,

)





class CategoryForm(forms.ModelForm):

    class Meta:

        model = Category

        fields = [
            "name",
            "display_name",
            "is_active",
        ]

        labels = {
            "name": "نام دسته‌بندی",
            "display_name": "نام نمایشی",
            "is_active": "دسته‌بندی فعال باشد",
        }

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام دسته‌بندی",
                }
            ),

            "display_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام نمایشی",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }



# ==========================
# Brand Form
# ==========================


class BrandForm(forms.ModelForm):

    class Meta:

        model = Brand

        fields = [
            "name",
            "display_name",
            "is_active",
        ]

        labels = {
            "name": "نام برند",
            "display_name": "نام نمایشی",
            "is_active": "برند فعال باشد",
        }

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام برند",
                }
            ),

            "display_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام نمایشی",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

        }


# ==========================
# Color Form
# ==========================


class ColorForm(forms.ModelForm):

    class Meta:

        model = Color

        fields = [
            "name",
            "display_name",
        ]

        labels = {
            "name": "نام رنگ",
            "display_name": "نام نمایشی",
        }

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام رنگ",
                }
            ),

            "display_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام نمایشی",
                }
            ),

        }