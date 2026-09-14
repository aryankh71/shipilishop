from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, CustomerProfile, Address


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Information", {
            "fields": ("phone_number", "role"),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Information", {
            "fields": ("phone_number", "role"),
        }),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "first_name",
        "last_name",
        "created_at",
    )

    search_fields = (
        "user__username",
        "first_name",
        "last_name",
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "title",
        "receiver_name",
        "city",
        "is_default",
    )

    list_filter = (
        "province",
        "city",
        "is_default",
    )

    search_fields = (
        "user__username",
        "receiver_name",
        "phone_number",
        "postal_code",
    )