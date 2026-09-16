from django.db import models

from apps.shop.models import (
    Product,
    ProductVariant,
    Category,
    Brand,
)


def get_product_stats():

    return {

        "total_products": Product.objects.count(),

        "active_products": Product.objects.filter(
            is_active=True
        ).count(),

        "total_variants": ProductVariant.objects.count(),

        "total_categories": Category.objects.count(),

        "total_brands": Brand.objects.count(),

        "out_of_stock": ProductVariant.objects.filter(
            stock=0
        ).count(),

        "low_stock_products": ProductVariant.objects.filter(
            stock__lte=models.F("low_stock_threshold")
        ).count(),

    }