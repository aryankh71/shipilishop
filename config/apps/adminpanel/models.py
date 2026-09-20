from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType


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



class ProductDeletionLog(models.Model):

    product = models.ForeignKey(
        "shop.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deletion_logs",
        verbose_name="محصول"
    )

    deleted_product_id = models.PositiveBigIntegerField(
        verbose_name="شناسه محصول"
    )

    product_name = models.CharField(
        max_length=200,
        verbose_name="نام محصول"
    )

    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_deletion_logs",
        verbose_name="حذف توسط"
    )

    ip_address = models.GenericIPAddressField(
        verbose_name="IP"
    )

    deleted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ و ساعت حذف"
    )

    class Meta:
        ordering = ["-deleted_at"]
        verbose_name = "لاگ حذف محصول"
        verbose_name_plural = "لاگ حذف محصولات"

    def __str__(self):
        return f"{self.product_name} - {self.deleted_by}"



class CatalogRecordLock(models.Model):

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="catalog_record_locks",
    )

    object_id = models.PositiveBigIntegerField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="catalog_record_locks",
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
    )

    last_activity = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "content_type",
                    "object_id",
                ],
                name="unique_catalog_record_lock",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "content_type",
                    "object_id",
                ]
            ),
            models.Index(
                fields=[
                    "last_activity",
                ]
            ),
        ]

        verbose_name = "قفل رکورد کاتالوگ"
        verbose_name_plural = "قفل‌های رکورد کاتالوگ"

    def __str__(self):
        return (
            f"{self.content_type.model} "
            f"#{self.object_id} - "
            f"{self.user.username}"
        )