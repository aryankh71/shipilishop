from datetime import timedelta

from django.db import models
from django.utils import timezone

from apps.account.models import User
from apps.shop.models import ProductVariant



class Cart(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CHECKOUT = "CHECKOUT", "Checkout"
        COMPLETED = "COMPLETED", "Completed"
        EXPIRED = "EXPIRED", "Expired"
        CANCELLED = "CANCELLED", "Cancelled"
        ABANDONED = "ABANDONED", "Abandoned"


    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="carts"
    )


    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )


    expires_at = models.DateTimeField(
        null=True,
        blank=True
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user"
                ],
                condition=models.Q(
                    status="ACTIVE"
                ),
                name="unique_active_cart_per_user"
            )
        ]


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


    @property
    def is_expired(self):

        if not self.expires_at:
            return False

        return (
            self.expires_at < timezone.now()
            and self.status not in [
                self.Status.COMPLETED,
                self.Status.CANCELLED
            ]
        )


    @property
    def has_pending_order(self):

        return hasattr(
            self,
            "order"
        ) and self.order.status == "PENDING_PAYMENT"
    


    def save(self, *args, **kwargs):

        if not self.expires_at:

            self.expires_at = (
                timezone.now()
                + timedelta(days=30)
            )

        super().save(*args, **kwargs)

    @classmethod
    def get_active_cart(cls, user):
        cart = cls.objects.filter(
            user=user,
            status=cls.Status.ACTIVE
        ).first()


        if cart:
            return cart


        # اگر سبد Active نبود،
        # سبدی که سفارش پرداخت نشده دارد برگردان

        cart = cls.objects.filter(
            user=user,
            status=cls.Status.CHECKOUT,
            order__status="PENDING_PAYMENT"
        ).first()


        return cart

    def __str__(self):

        return f"{self.user.username} Cart"






class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )


    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="cart_items"
    )


    quantity = models.PositiveIntegerField(
        default=1
    )


    # قیمت زمان اضافه شدن به سبد
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "cart",
                    "variant"
                ],
                name="unique_cart_variant"
            )
        ]

        ordering = [
            "-created_at"
        ]



    @property
    def total_price(self):

        return self.unit_price * self.quantity



    def save(self, *args, **kwargs):

        if not self.unit_price:

            self.unit_price = self.variant.price

        super().save(*args, **kwargs)



    def __str__(self):

        return f"{self.variant.sku_name} x {self.quantity}"