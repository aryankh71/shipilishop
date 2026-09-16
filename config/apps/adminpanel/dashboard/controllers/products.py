from django.shortcuts import render

from apps.shop.models import Product
from ...decorators import admin_required

@admin_required
def product_list(request):

    products = (
        Product.objects
        .select_related(
            "category",
            "brand"
        )
        .prefetch_related(
            "variants"
        )
        .all()
    )


    context = {

        "products": products

    }


    return render(
        request,
        "adminpanel/products/list.html",
        context
    )