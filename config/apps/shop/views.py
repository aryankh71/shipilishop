from django.shortcuts import render
from apps.shop.models import ProductVariant
from apps.cart.models import Cart


def home(request):

    variants = ProductVariant.objects.filter(
        is_active=True,
        product__is_active=True,
    ).select_related(
        "product",
        "color",
    )

    cart_count = 0

    if request.user.is_authenticated:

        cart = Cart.get_active_cart(request.user)

        if cart:
            cart_count = cart.total_items

    return render(
        request,
        "shop/home.html",
        {
            "variants": variants,
            "cart_count": cart_count,
        },
    )