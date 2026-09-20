import random
import re
from django.utils.text import slugify
from unidecode import unidecode


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

    text = unidecode(
        value.strip()
    )

    words = re.findall(
        r"[A-Za-z]+",
        text
    )

    if not words:
        return "GEN"

    # -----------------------------------
    # Multi-word category
    # -----------------------------------

    if len(words) > 1:

        code = "".join(
            word[0]
            for word in words
        )

    # -----------------------------------
    # Single-word category
    # -----------------------------------

    else:

        word = words[0].upper()

        # حذف حروف صدادار
        consonants = re.sub(
            r"[AEIOU]",
            "",
            word
        )

        if len(consonants) >= 4:
            code = consonants[:4]

        else:
            code = word[:4]

    return code[:4].upper() or "GEN"


def generate_unique_code(value, model, instance=None):

    base_code = generate_code(value)

    code = base_code
    counter = 2

    queryset = model.objects.all()

    if instance and instance.pk:
        queryset = queryset.exclude(
            pk=instance.pk
        )

    while queryset.filter(code=code).exists():

        suffix = str(counter)

        code = (
            base_code[:4 - len(suffix)]
            + suffix
        )

        counter += 1

    return code

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