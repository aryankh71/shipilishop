import random
import re
from django.utils.text import slugify


# -----------------------------------
# Generate Barcode
# -----------------------------------

def generate_barcode():
    return str(
        random.randint(
            100000000000,
            999999999999
        )
    )


# -----------------------------------
# Generate Slug
# -----------------------------------

def generate_slug(value):

    if not value:
        return ""

    value = value.strip()

    # English slug
    slug = slugify(value)

    if slug:
        return slug

    # Persian fallback
    slug = re.sub(
        r"\s+",
        "-",
        value
    )

    slug = re.sub(
        r"[^\w\-]",
        "",
        slug
    )

    return slug.lower()



# -----------------------------------
# Generate Code
# -----------------------------------

def generate_code(value):

    if not value:
        return "GEN"


    value = value.strip()


    # حذف فاصله و کاراکترهای اضافی
    clean = (
        value
        .replace("-", "")
        .replace(" ", "")
        .upper()
    )


    # اگر انگلیسی بود
    english = "".join(
        c for c in clean
        if c.isascii()
        and c.isalpha()
    )


    if english:
        return english[:3]


    # فارسی:
    # سه حرف اول
    return clean[:3].upper()



# -----------------------------------
# Generate SKU
# -----------------------------------

def generate_sku(product, color):

    category_code = (
        product.category.code.upper()
        if product.category.code
        else "GEN"
    )


    brand_code = (
        product.brand.code.upper()
        if product.brand.code
        else "GEN"
    )


    color_code = (
        color.code.upper()
        if color.code
        else "GEN"
    )


    prefix = (
        f"{category_code}-"
        f"{brand_code}-"
        f"{color_code}"
    )


    from .models import ProductVariant


    last_variant = (
        ProductVariant.objects
        .filter(
            sku_code__startswith=prefix
        )
        .order_by("-id")
        .first()
    )


    if last_variant:

        last_number = int(
            last_variant.sku_code.split("-")[-1]
        )

        number = last_number + 1

    else:

        number = 1



    return (
        f"{prefix}-"
        f"{number:06d}"
    )