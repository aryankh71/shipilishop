from django.db import models
from decimal import Decimal


class Payment(models.Model):


    # =========================================
    # Payment Status
    # =========================================

    class Status(models.TextChoices):

        CREATED = (
            "CREATED",
            "Created"
        )


        PENDING = (
            "PENDING",
            "Pending"
        )


        SUCCESS = (
            "SUCCESS",
            "Success"
        )


        FAILED = (
            "FAILED",
            "Failed"
        )


        CANCELLED = (
            "CANCELLED",
            "Cancelled"
        )


    # =========================================
    # Payment Provider
    # =========================================

    class Provider(models.TextChoices):

        ZARINPAL = (
            "ZARINPAL",
            "ZarinPal"
        )


    # =========================================
    # Order
    # =========================================

    order = models.OneToOneField(
        "order.Order",
        on_delete=models.PROTECT,
        related_name="payment"
    )


    # =========================================
    # Provider
    # =========================================

    provider = models.CharField(
        max_length=30,
        choices=Provider.choices,
        default=Provider.ZARINPAL
    )


    # =========================================
    # Amount Snapshot
    # =========================================

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )


    # =========================================
    # Payment Status
    # =========================================

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED
    )


    # =========================================
    # Gateway Authority / Token
    # =========================================

    authority = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True
    )


    # =========================================
    # Final Gateway Reference ID
    # =========================================

    reference_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True
    )


    # =========================================
    # Gateway Response
    # =========================================

    gateway_response = models.JSONField(
        blank=True,
        null=True
    )


    # =========================================
    # Failure Reason
    # =========================================

    failure_reason = models.TextField(
        blank=True,
        null=True
    )


    # =========================================
    # Dates
    # =========================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    # =========================================
    # Ordering
    # =========================================

    class Meta:

        ordering = [
            "-created_at"
        ]


        indexes = [

            models.Index(
                fields=[
                    "status",
                    "created_at"
                ]
            ),

        ]


    # =========================================
    # String Representation
    # =========================================

    def __str__(self):

        return (
            f"Payment #{self.pk} | "
            f"Order #{self.order_id} | "
            f"{self.status}"
        )