from django.db import models
from decimal import Decimal
from apps.account.models import User, Address
from apps.shop.models import ProductVariant
from apps.cart.models import Cart


class Order(models.Model):

    class Status(models.TextChoices):

        PENDING_PAYMENT = (
            "PENDING_PAYMENT",
            "Pending Payment"
        )

        PAID = (
            "PAID",
            "Paid"
        )

        PAYMENT_FAILED = (
            "PAYMENT_FAILED",
            "Payment Failed"
        )

        CANCELLED = (
            "CANCELLED",
            "Cancelled"
        )

        EXPIRED = (
            "EXPIRED",
            "Expired"
        )


    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    cart = models.OneToOneField(
    Cart,
    on_delete=models.PROTECT,
    related_name="order",

)


    address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        related_name="orders"
    )


    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    @property
    def total_items(self):

        return sum(
            item.quantity
            for item in self.items.all()
        )


    @property
    def total_price(self):

        return sum(
            item.total_price
            for item in self.items.all()
        )

    def clean(self):

        from django.core.exceptions import ValidationError
    
        if self.address and self.user:
        
            if self.address.user_id != self.user_id:
            
                raise ValidationError({
                    "address": (
                        "آدرس انتخاب شده متعلق به این کاربر نیست."
                    )
                })
    


    def __str__(self):

        return (
            f"Order #{self.pk} - "
            f"{self.user.username}"
        )


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )


    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="order_items"
    )


    quantity = models.PositiveIntegerField()


    # Snapshot قیمت در زمان ایجاد سفارش
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    class Meta:

        ordering = [
            "-created_at"
        ]


        constraints = [

            models.UniqueConstraint(
                fields=[
                    "order",
                    "variant"
                ],
                name="unique_order_variant"
            )

        ]


    @property
    def total_price(self):
    
        if self.unit_price is None or self.quantity is None:
            return Decimal("0")
    
        return self.unit_price * self.quantity


    def __str__(self):

        return (
            f"{self.variant.sku_name} "
            f"x {self.quantity}"
        )