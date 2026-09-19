from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from apps.shop.models import Product
from django.contrib import messages

from ...decorators import admin_required
from ...forms import (
    ProductForm,
    ProductVariantFormSet,
)



@admin_required
def product_list(request):

    products = (
        Product.objects
        .select_related(
            "category",
            "brand"
        )
        .annotate(
            variant_count=Count("variants")
        )
    )


    context = {

        "products": products

    }


    return render(
        request,
        "adminpanel/products/list.html",
        context
    )



@admin_required
def product_edit(request, product_id):

    product = get_object_or_404(
        Product.objects
        .select_related(
            "category",
            "brand"
        )
        .prefetch_related(
            "variants__color"
        ),
        id=product_id
    )


    if request.method == "POST":


        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )


        variant_formset = ProductVariantFormSet(
            request.POST,
            instance=product
        )



        if form.is_valid() and variant_formset.is_valid():


            product = form.save()


            variant_formset.save()



            messages.success(
                request,
                "تغییرات محصول با موفقیت ذخیره شد."
            )


            return redirect(
                "adminpanel:product_edit",
                product_id=product.id
            )



        else:
            print("PRODUCT FORM ERRORS:")
            print(form.errors)
            print("VARIANT FORMSET ERRORS:")
            print(variant_formset.errors)


            messages.error(
                request,
                "ذخیره تغییرات انجام نشد. لطفاً اطلاعات وارد شده را بررسی کنید."
            )



    else:


        form = ProductForm(
            instance=product
        )


        variant_formset = ProductVariantFormSet(
            instance=product
        )



    context = {

        "product": product,

        "form": form,

        "variant_formset": variant_formset,

    }



    return render(
        request,
        "adminpanel/products/edit.html",
        context
    )