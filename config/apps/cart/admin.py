from django.contrib import admin

from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "status",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "user__username",
    )



@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        "cart",
        "variant",
        "quantity",
        "unit_price",
        "total_price_display",
    )


    search_fields = (
        "variant__sku_code",
        "variant__sku_name",
        "cart__user__username",
    )


    def total_price_display(self, obj):
        return obj.total_price


    total_price_display.short_description = "قیمت کل"