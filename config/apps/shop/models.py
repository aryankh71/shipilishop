from django.db import models
from .utils import (
    generate_sku,
    generate_barcode,
    generate_slug,
    generate_code,
)


class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    display_name = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    code = models.CharField(
        max_length=3,
        unique=True,
        null=True,
        blank=True
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    def save(self, *args, **kwargs):

        if not self.code:
            self.code = generate_code(
                self.display_name or self.name
            )

        if not self.slug:
            self.slug = generate_slug(
                self.display_name or self.name
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name



class Brand(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    display_name = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    code = models.CharField(
        max_length=3,
        unique=True,
        null=True,
        blank=True
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    def save(self, *args, **kwargs):

        if not self.code:
            self.code = generate_code(
                self.display_name or self.name
            )

        if not self.slug:
            self.slug = generate_slug(
                self.display_name or self.name
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name



class Color(models.Model):

    name = models.CharField(
        max_length=50,
        unique=True
    )

    display_name = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    code = models.CharField(
        max_length=3,
        unique=True
    )


    def save(self, *args, **kwargs):

        if not self.code:
            self.code = generate_code(
                self.display_name or self.name
            )

        super().save(*args, **kwargs)    

    def __str__(self):
        return self.display_name



class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="products"
    )


    name = models.CharField(
        max_length=200
    )

    display_name = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )


    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True
    )


    description = models.TextField(
        blank=True
    )


    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )


    is_active = models.BooleanField(
        default=True
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = generate_slug(
                self.display_name or self.name
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name



class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )


    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        related_name="variants"
    )


    size = models.CharField(
        max_length=50,
        blank=True
    )


    sku_code = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )


    sku_name = models.CharField(
        max_length=255,
        blank=True
    )


    barcode = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )


    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )


    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی کل"
    )


    reserved_stock = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی رزرو شده"
    )


    low_stock_threshold = models.PositiveIntegerField(
        default=5,
        verbose_name="حد هشدار موجودی"
    )


    is_active = models.BooleanField(
        default=True
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    def save(self, *args, **kwargs):

        if not self.sku_code:
            self.sku_code = generate_sku(
                self.product,
                self.color
            )


        if not self.barcode:
            self.barcode = generate_barcode()


        self.sku_name = (
            f"{self.product.display_name or self.product.name} "
            f"{self.color.display_name or self.color.name}"
        )


        if self.size:
            self.sku_name += f" {self.size}"


        super().save(*args, **kwargs)

    
    @property
    def available_stock(self):
        """
        موجودی قابل فروش
        """
        return max(
            self.stock - self.reserved_stock,
            0
        )
    
    
    @property
    def stock_status(self):
        """
        وضعیت موجودی
        """
    
        if self.available_stock == 0:
            return "ناموجود"
    
        elif self.available_stock <= self.low_stock_threshold:
            return "رو به اتمام"
    
        return "موجود"
    


    def __str__(self):
        return self.sku_name