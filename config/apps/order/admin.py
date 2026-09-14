from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):

    model = OrderItem
    extra = 0

    readonly_fields = (
        "variant",
        "quantity",
        "unit_price",
        "total_price_display",
    )

    def total_price_display(self, obj):

        return obj.total_price

    total_price_display.short_description = (
        "Total Price"
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "status",
        "total_items_display",
        "total_price_display",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__phone_number",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "total_items_display",
        "total_price_display",
    )

    inlines = [
        OrderItemInline
    ]


    def total_items_display(self, obj):

        return obj.total_items

    total_items_display.short_description = (
        "Total Items"
    )


    def total_price_display(self, obj):

        return obj.total_price

    total_price_display.short_description = (
        "Total Price"
    )