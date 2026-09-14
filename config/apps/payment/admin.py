from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "provider",
        "amount",
        "status",
        "reference_id",
        "created_at",
    )


    list_filter = (
        "status",
        "provider",
    )


    search_fields = (
        "id",
        "authority",
        "reference_id",
        "order__id",
        "order__user__username",
    )


    readonly_fields = (
        "created_at",
        "updated_at",
    )


    ordering = (
        "-created_at",
    )