from django.contrib import admin

from .models import (
    Category,
    Brand,
    Color,
    Product,
    ProductVariant,
)



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "display_name",
        "code",
        "slug",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "display_name",
        "code",
    )



@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "display_name",
        "code",
        "slug",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "display_name",
        "code",
    )



@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "display_name",
        "code",
    )

    search_fields = (
        "name",
        "display_name",
        "code",
    )



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "display_name",
        "category",
        "brand",
        "is_active",
    )

    list_filter = (
        "category",
        "brand",
        "is_active",
    )

    search_fields = (
        "name",
        "display_name",
        "slug",
    )



@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "sku_code",
        "sku_name",
        "barcode",
        "color",
        "price",
        "stock",
        "reserved_stock",
        "available_stock_display",
        "stock_status_display",
        "is_active",
    )

    readonly_fields = (
        "sku_code",
        "sku_name",
        "barcode",
    )

    list_filter = (
        "color",
        "is_active",
    )

    search_fields = (
        "sku_code",
        "sku_name",
        "barcode",
        "product__name",
    )


    
    def available_stock_display(self, obj):
        return obj.available_stock
    
    available_stock_display.short_description = "موجودی قابل فروش"
    
    
    
    def stock_status_display(self, obj):
        return obj.stock_status
    
    stock_status_display.short_description = "وضعیت موجودی"