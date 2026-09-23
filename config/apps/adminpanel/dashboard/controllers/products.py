from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from apps.shop.models import Product
from django.contrib import messages
from datetime import time
from django.db import transaction
from django.utils import timezone
from apps.adminpanel.models import ProductDeletionLog
from django.http import JsonResponse

from apps.adminpanel.services import (
    acquire_catalog_lock,
    release_catalog_lock,
    refresh_catalog_lock,
)

from ...decorators import admin_required
from ...forms import (
    ProductForm,
    ProductVariantFormSet,
)



def get_client_ip(request):

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")

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

    try:
        if request.method == "POST":
            refresh_catalog_lock(
                record=product,
                user=request.user,
                )
        else:
            acquire_catalog_lock(
                record=product,
                user=request.user,
            )
    except (ValueError, PermissionError) as exc:

        messages.error(
            request,
            str(exc),
        )

        return redirect(
            "adminpanel:products"
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


            # release_catalog_lock(
            #     record=product,
            #     user=request.user,
            # )

            messages.success(
                request,
                "تغییرات محصول با موفقیت ذخیره شد."
            )


            return redirect(
                "adminpanel:product_edit",
                product_id=product.id
            )



        else:


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



@admin_required
def product_create(request):

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            product = form.save()

            messages.success(
                request,
                "محصول با موفقیت ایجاد شد."
            )

            return redirect(
                "adminpanel:product_edit",
                product_id=product.id
            )

        else:

            messages.error(
                request,
                "ایجاد محصول انجام نشد. لطفاً اطلاعات وارد شده را بررسی کنید."
            )

    else:

        form = ProductForm()

    context = {

        "form": form,

    }

    return render(
        request,
        "adminpanel/products/create.html",
        context
    )

@admin_required
def product_delete(request, product_id):

    if request.method != "POST":
        return redirect(
            "adminpanel:products"
        )

    now = timezone.localtime()

    current_time = now.time()

    if not (
        time(9, 0) <= current_time < time(17, 0)
    ):
        messages.error(
            request,
            "حذف محصول فقط بین ساعت 09:00 تا 17:00 امکان‌پذیر است."
        )

        return redirect(
            "adminpanel:products"
        )

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    ip_address = get_client_ip(request)

    with transaction.atomic():

        product.is_active = False

        product.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        ProductDeletionLog.objects.create(
            product=product,
            deleted_product_id=product.id,
            product_name=product.name,
            deleted_by=request.user,
            ip_address=ip_address,
        )

    messages.success(
        request,
        "محصول با موفقیت حذف شد."
    )

    return redirect(
        "adminpanel:products"
    )



@admin_required
def product_release_lock(request, product_id):
    if request.method != "POST":
        return JsonResponse(
            {"success": False},
            status=405
        )

    product = get_object_or_404(
        Product,
        id=product_id
    )

    try:
        release_catalog_lock(
            record=product,
            user=request.user,
        )
    except (ValueError, PermissionError):
        return JsonResponse(
            {"success": False},
            status=403
        )

    return JsonResponse(
        {"success": True}
    )
