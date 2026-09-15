from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    AdminAccess,
    AdminOTP,
    AdminRequest,
)


# =========================================================
# Admin Request
# =========================================================

@admin.register(AdminRequest)
class AdminRequestAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "status",
        "created_at",
        "token_issued_at",
        "approved_at",
        "approve_button",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "user__phone_number",
    )

    readonly_fields = (
        "user",
        "token_hash",
        "created_at",
        "token_issued_at",
        "approved_at",
        "rejected_at",
    )

    fieldsets = (

        (
            "اطلاعات درخواست",
            {
                "fields": (
                    "user",
                    "status",
                )
            }
        ),

        (
            "اطلاعات Token",
            {
                "fields": (
                    "token_hash",
                    "token_issued_at",
                )
            }
        ),

        (
            "تاریخ‌ها",
            {
                "fields": (
                    "created_at",
                    "approved_at",
                    "rejected_at",
                )
            }
        ),

    )

    # -----------------------------------------------------
    # Approve Token Button
    # -----------------------------------------------------

    @admin.display(
        description="عملیات",
        ordering=False,
    )
    def approve_button(self, obj):

        if obj.status != AdminRequest.Status.TOKEN_ISSUED:
            return "-"

        url = reverse(
            "adminpanel:approve_admin_access",
            args=[obj.id],
        )

        return format_html(
            '<a class="button" href="{}">'
            'تأیید Token'
            '</a>',
            url,
        )


# =========================================================
# Admin OTP
# =========================================================

@admin.register(AdminOTP)
class AdminOTPAdmin(admin.ModelAdmin):

    list_display = (
        "request",
        "attempts",
        "created_at",
        "expires_at",
        "verified_at",
    )

    list_filter = (
        "verified_at",
        "created_at",
    )

    search_fields = (
        "request__user__username",
        "request__user__email",
    )

    readonly_fields = (
        "request",
        "otp_hash",
        "attempts",
        "created_at",
        "expires_at",
        "verified_at",
    )

    fieldsets = (

        (
            "اطلاعات OTP",
            {
                "fields": (
                    "request",
                    "attempts",
                )
            }
        ),

        (
            "Security",
            {
                "fields": (
                    "otp_hash",
                    "created_at",
                    "expires_at",
                    "verified_at",
                )
            }
        ),

    )


# =========================================================
# Admin Access
# =========================================================

@admin.register(AdminAccess)
class AdminAccessAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "status",
        "created_at",
        "revoked_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "user__phone_number",
    )

    readonly_fields = (
        "request",
        "user",
        "token_hash",
        "created_at",
        "revoked_at",
    )

    fieldsets = (

        (
            "Owner",
            {
                "fields": (
                    "user",
                    "request",
                )
            }
        ),

        (
            "Access Security",
            {
                "fields": (
                    "status",
                    "token_hash",
                )
            }
        ),

        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "revoked_at",
                )
            }
        ),

    )

    actions = [
        "revoke_access",
    ]

    # -----------------------------------------------------
    # Revoke Access
    # -----------------------------------------------------

    @admin.action(
        description="لغو دسترسی ادمین انتخاب شده"
    )
    def revoke_access(
        self,
        request,
        queryset,
    ):

        updated = queryset.filter(
            status=AdminAccess.Status.ACTIVE
        ).update(
            status=AdminAccess.Status.REVOKED,
            revoked_at=timezone.now(),
        )

        self.message_user(
            request,
            f"{updated} دسترسی لغو شد.",
        )