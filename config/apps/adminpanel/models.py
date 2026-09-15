from django.conf import settings
from django.db import models


class AdminRequest(models.Model):

    class Status(models.TextChoices):
        PENDING_OTP = "PENDING_OTP", "در انتظار OTP"
        OTP_VERIFIED = "OTP_VERIFIED", "OTP تأیید شده"
        TOKEN_ISSUED = "TOKEN_ISSUED", "توکن صادر شده"
        APPROVED = "APPROVED", "تأیید شده"
        REJECTED = "REJECTED", "رد شده"
        CANCELLED = "CANCELLED", "لغو شده"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_requests",
    )

    token_hash = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        unique=True,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING_OTP,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    token_issued_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.user.username} - {self.status}"


class AdminOTP(models.Model):

    request = models.ForeignKey(
        AdminRequest,
        on_delete=models.CASCADE,
        related_name="otps",
    )

    otp_hash = models.CharField(
        max_length=128,
    )

    attempts = models.PositiveSmallIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_at = models.DateTimeField()

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.request.user.username} - OTP"


class AdminAccess(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "فعال"
        REVOKED = "REVOKED", "لغو شده"

    request = models.OneToOneField(
        AdminRequest,
        on_delete=models.CASCADE,
        related_name="access",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_accesses",
    )

    # Token approved by Superuser
    token_hash = models.CharField(
        max_length=128,
        unique=True,
    )

    # Separate secret used only inside Dynamic URL
    url_secret_hash = models.CharField(
        max_length=128,
        unique=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.user.username} - {self.status}"