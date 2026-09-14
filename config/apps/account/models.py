from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        CUSTOMER = "CUSTOMER", "Customer"

    phone_number = models.CharField(
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^09\d{9}$",
                message="شماره موبایل باید به صورت 09xxxxxxxxx وارد شود.",
            )
        ],
    )

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )

    def __str__(self):
        return self.username


class Address(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    title = models.CharField(
        max_length=50,
        default="خانه"
    )

    receiver_name = models.CharField(
        max_length=150
    )

    phone_number = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r"^09\d{9}$",
                message="شماره موبایل باید به صورت 09xxxxxxxxx وارد شود."
            )
        ]
    )

    province = models.CharField(
        max_length=100
    )

    city = models.CharField(
        max_length=100
    )

    address = models.TextField()

    postal_code = models.CharField(
        max_length=10
    )

    is_default = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    @property
    def is_complete(self):
        return all([
            self.receiver_name,
            self.phone_number,
            self.province,
            self.city,
            self.address,
            self.postal_code,
        ])


    def save(self, *args, **kwargs):

        if self.is_default:
            Address.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(
                id=self.id
            ).update(
                is_default=False
            )

        super().save(*args, **kwargs)


    class Meta:
        indexes = [
            models.Index(
                fields=["user", "is_default"]
            )
        ]


    def __str__(self):
        return f"{self.user.username} - {self.title}"



class CustomerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    first_name = models.CharField(
        max_length=100,
        blank=True
    )

    last_name = models.CharField(
        max_length=100,
        blank=True
    )

    national_code = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True
    )

    avatar = models.ImageField(
        upload_to="profile/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    def __str__(self):
        return f"{self.first_name} {self.last_name}"