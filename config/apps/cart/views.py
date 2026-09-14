from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import JsonResponse
from .models import Cart, CartItem
from apps.shop.models import ProductVariant


# =========================================================
# Guest Cart Helpers
# =========================================================

GUEST_CART_SESSION_KEY = "guest_cart"


def get_guest_cart(request):
    """
    سبد خرید کاربر مهمان را از Session برمی‌گرداند.


    ساختار Session:

    {
        "12": 2,
        "18": 1,
        "25": 3
    }

    یعنی:
    variant_id = 12 -> quantity = 2
    """

    return request.session.get(
        GUEST_CART_SESSION_KEY,
        {}
    )


def save_guest_cart(request, cart):
    """
    ذخیره سبد مهمان در Session
    """

    request.session[
        GUEST_CART_SESSION_KEY
    ] = cart

    request.session.modified = True


def clear_guest_cart(request):
    """
    پاک کردن سبد مهمان
    """

    request.session.pop(
        GUEST_CART_SESSION_KEY,
        None
    )

    request.session.modified = True


def get_guest_cart_items(request):
    """
    تبدیل اطلاعات Session به لیست محصولات واقعی.
    """

    session_cart = get_guest_cart(request)

    if not session_cart:
        return []


    variant_ids = [
        int(variant_id)
        for variant_id in session_cart.keys()
    ]


    variants = ProductVariant.objects.select_related(
        "product",
        "color"
    ).filter(
        id__in=variant_ids
    )


    items = []


    for variant in variants:

        quantity = int(
            session_cart.get(
                str(variant.id),
                0
            )
        )


        if quantity <= 0:
            continue


        items.append({
            "variant": variant,
            "quantity": quantity,
            "unit_price": variant.price,
            "total_price": (
                variant.price * quantity
            )
        })


    return items


def get_guest_cart_count(request):
    """
    تعداد کل محصولات داخل سبد مهمان
    """

    session_cart = get_guest_cart(request)

    return sum(
        int(quantity)
        for quantity in session_cart.values()
    )


def sync_cart_prices(cart):
    """
    هماهنگ کردن قیمت CartItem با قیمت فعلی ProductVariant
    """

    items = cart.items.select_related(
        "variant"
    )

    for item in items:

        current_price = item.variant.price

        if item.unit_price != current_price:

            item.unit_price = current_price

            item.save(
                update_fields=[
                    "unit_price",
                    "updated_at",
                ]
            )
# =========================================================
# Cart Detail
# =========================================================

def cart_detail(request):

    # =====================================================
    # Logged In User
    # =====================================================

    if request.user.is_authenticated:

        cart = Cart.get_active_cart(
            request.user
        )

        if cart:

            sync_cart_prices(
                cart
            )


        return render(
            request,
            "cart/cart_detail.html",
            {
                "cart": cart,
                "guest_cart": False,
            }
        )


    # =====================================================
    # Guest User
    # =====================================================

    guest_items = get_guest_cart_items(
        request
    )


    guest_total_items = sum(
        item["quantity"]
        for item in guest_items
    )


    guest_total_price = sum(
        item["total_price"]
        for item in guest_items
    )


    return render(
        request,
        "cart/cart_detail.html",
        {
            "cart": None,
            "guest_cart": True,
            "guest_items": guest_items,
            "guest_total_items": guest_total_items,
            "guest_total_price": guest_total_price,
        }
    )


# =========================================================
# Add To Cart
# =========================================================

@require_POST
def add_to_cart(request, variant_id):

    is_ajax = (
        request.headers.get(
            "X-Requested-With"
        )
        == "XMLHttpRequest"
    )

    next_url = request.POST.get(
        "next"
    )

    if not next_url:

        next_url = reverse(
            "home"
        )

    variant = get_object_or_404(
        ProductVariant,
        id=variant_id
    )

    # =====================================================
    # Stock Check
    # =====================================================

    if variant.available_stock <= 0:

        error_message = (
            "این محصول در حال حاضر موجود نیست."
        )

        if is_ajax:

            return JsonResponse(
                {
                    "success": False,
                    "message": error_message,
                },
                status=400
            )

        messages.error(
            request,
            error_message
        )

        return redirect(
            next_url
        )

    # =====================================================
    # Logged In User
    # =====================================================

    if request.user.is_authenticated:

        cart = Cart.get_active_cart(
            request.user
        )

        if not cart:

            cart = Cart.objects.create(
                user=request.user,
                status=Cart.Status.ACTIVE
            )

        cart_item = CartItem.objects.filter(
            cart=cart,
            variant=variant
        ).first()

        if cart_item:

            if (
                cart_item.quantity + 1
                > variant.available_stock
            ):

                error_message = (
                    "تعداد درخواستی بیشتر از موجودی قابل فروش است."
                )

                if is_ajax:

                    return JsonResponse(
                        {
                            "success": False,
                            "message": error_message,
                            "cart_count": cart.total_items,
                        },
                        status=400
                    )

                messages.error(
                    request,
                    error_message
                )

                return redirect(
                    next_url
                )

            cart_item.quantity += 1

            cart_item.save()

        else:

            CartItem.objects.create(
                cart=cart,
                variant=variant,
                quantity=1
            )

        success_message = (
            "محصول با موفقیت به سبد خرید اضافه شد."
        )

        if is_ajax:

            cart.refresh_from_db()

            return JsonResponse(
                {
                    "success": True,
                    "message": success_message,
                    "cart_count": cart.total_items,
                }
            )

        messages.success(
            request,
            success_message
        )

        return redirect(
            next_url
        )

    # =====================================================
    # Guest User
    # =====================================================

    guest_cart = get_guest_cart(
        request
    )

    variant_key = str(
        variant.id
    )

    current_quantity = int(
        guest_cart.get(
            variant_key,
            0
        )
    )

    if (
        current_quantity + 1
        > variant.available_stock
    ):

        error_message = (
            "تعداد درخواستی بیشتر از موجودی قابل فروش است."
        )

        if is_ajax:

            return JsonResponse(
                {
                    "success": False,
                    "message": error_message,
                    "cart_count": get_guest_cart_count(
                        request
                    ),
                },
                status=400
            )

        messages.error(
            request,
            error_message
        )

        return redirect(
            next_url
        )

    guest_cart[
        variant_key
    ] = current_quantity + 1

    save_guest_cart(
        request,
        guest_cart
    )

    success_message = (
        "محصول با موفقیت به سبد خرید اضافه شد."
    )

    if is_ajax:

        return JsonResponse(
            {
                "success": True,
                "message": success_message,
                "cart_count": get_guest_cart_count(
                    request
                ),
            }
        )

    messages.success(
        request,
        success_message
    )

    return redirect(
        next_url
    )




# =========================================================
# Increase Cart Item
# =========================================================

@require_POST
def increase_cart_item(
    request,
    item_id
):

    # =====================================================
    # Logged In User
    # =====================================================

    if request.user.is_authenticated:

        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user,
            cart__status=Cart.Status.ACTIVE
        )


        if (
            cart_item.quantity + 1
            > cart_item.variant.available_stock
        ):

            messages.error(
                request,
                "تعداد درخواستی بیشتر از موجودی قابل فروش است."
            )

            return redirect(
                "cart_detail"
            )


        cart_item.quantity += 1

        cart_item.save()


        messages.success(
            request,
            "تعداد محصول افزایش یافت."
        )


        return redirect(
            "cart_detail"
        )


    # =====================================================
    # Guest User
    # =====================================================

    guest_cart = get_guest_cart(
        request
    )


    variant_key = str(
        item_id
    )


    if variant_key not in guest_cart:

        messages.error(
            request,
            "محصول مورد نظر در سبد خرید وجود ندارد."
        )

        return redirect(
            "cart_detail"
        )


    variant = get_object_or_404(
        ProductVariant,
        id=item_id
    )


    current_quantity = int(
        guest_cart[variant_key]
    )


    if (
        current_quantity + 1
        > variant.available_stock
    ):

        messages.error(
            request,
            "تعداد درخواستی بیشتر از موجودی قابل فروش است."
        )

        return redirect(
            "cart_detail"
        )


    guest_cart[
        variant_key
    ] = current_quantity + 1


    save_guest_cart(
        request,
        guest_cart
    )


    messages.success(
        request,
        "تعداد محصول افزایش یافت."
    )


    return redirect(
        "cart_detail"
    )


# =========================================================
# Decrease Cart Item
# =========================================================

@require_POST
def decrease_cart_item(
    request,
    item_id
):

    # =====================================================
    # Logged In User
    # =====================================================

    if request.user.is_authenticated:

        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user,
            cart__status=Cart.Status.ACTIVE
        )


        if cart_item.quantity > 1:

            cart_item.quantity -= 1
            cart_item.save()


            messages.success(
                request,
                "تعداد محصول کاهش یافت."
            )

        else:

            cart_item.delete()


            messages.success(
                request,
                "محصول از سبد خرید حذف شد."
            )


        return redirect(
            "cart_detail"
        )


    # =====================================================
    # Guest User
    # =====================================================

    guest_cart = get_guest_cart(
        request
    )


    variant_key = str(
        item_id
    )


    if variant_key not in guest_cart:

        messages.error(
            request,
            "محصول مورد نظر در سبد خرید وجود ندارد."
        )

        return redirect(
            "cart_detail"
        )


    current_quantity = int(
        guest_cart[variant_key]
    )


    if current_quantity > 1:

        guest_cart[
            variant_key
        ] = current_quantity - 1


        messages.success(
            request,
            "تعداد محصول کاهش یافت."
        )

    else:

        del guest_cart[
            variant_key
        ]


        messages.success(
            request,
            "محصول از سبد خرید حذف شد."
        )


    save_guest_cart(
        request,
        guest_cart
    )


    return redirect(
        "cart_detail"
    )


# =========================================================
# Remove Cart Item
# =========================================================

@require_POST
def remove_cart_item(
    request,
    item_id
):

    # =====================================================
    # Logged In User
    # =====================================================

    if request.user.is_authenticated:

        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user,
            cart__status=Cart.Status.ACTIVE
        )


        product_name = str(
            cart_item.variant
        )


        cart_item.delete()


        messages.success(
            request,
            f"{product_name} از سبد خرید حذف شد."
        )


        return redirect(
            "cart_detail"
        )


    # =====================================================
    # Guest User
    # =====================================================

    guest_cart = get_guest_cart(
        request
    )


    variant_key = str(
        item_id
    )


    if variant_key not in guest_cart:

        messages.error(
            request,
            "محصول مورد نظر در سبد خرید وجود ندارد."
        )

        return redirect(
            "cart_detail"
        )


    variant = get_object_or_404(
        ProductVariant,
        id=item_id
    )


    product_name = str(
        variant
    )


    del guest_cart[
        variant_key
    ]


    save_guest_cart(
        request,
        guest_cart
    )


    messages.success(
        request,
        f"{product_name} از سبد خرید حذف شد."
    )


    return redirect(
        "cart_detail"
    )


# =========================================================
# Checkout
# =========================================================

def checkout(request):

    # =====================================================
    # Guest
    # =====================================================

    if not request.user.is_authenticated:

        guest_items = get_guest_cart_items(
            request
        )


        if not guest_items:

            messages.warning(
                request,
                "سبد خرید شما خالی است."
            )

            return redirect(
                "cart_detail"
            )


        # فعلاً Login را اجباری می‌کنیم.
        # در مرحله بعد می‌توانیم مودال را
        # قبل از ورود به این View باز کنیم.

        login_url = reverse(
            "login"
        )


        return redirect(
            f"{login_url}?next={reverse('checkout')}"
        )


    # =====================================================
    # Logged In User
    # =====================================================

    cart = Cart.get_active_cart(
        request.user
    )


    if not cart:

        messages.warning(
            request,
            "سبد خریدی وجود ندارد."
        )

        return redirect(
            "cart_detail"
        )


    if cart.is_expired:

        cart.status = Cart.Status.EXPIRED

        cart.save()


        messages.warning(
            request,
            "سبد خرید شما منقضی شده است."
        )

        return redirect(
            "cart_detail"
        )


    if not cart.items.exists():

        messages.warning(
            request,
            "سبد خرید شما خالی است."
        )

        return redirect(
            "cart_detail"
        )
    
    sync_cart_prices(
        cart
    )


    address = request.user.addresses.filter(
        is_default=True
    ).first()


    if not address or not address.is_complete:

        messages.warning(
            request,
            "لطفاً آدرس ارسال را تکمیل کنید."
        )


        address_create_url = reverse(
            "address_create"
        )


        checkout_url = reverse(
            "checkout"
        )


        return redirect(
            f"{address_create_url}?next={checkout_url}"
        )


    for item in cart.items.select_related(
        "variant"
    ):

        if (
            item.quantity
            > item.variant.available_stock
        ):

            messages.error(
                request,
                f"موجودی {item.variant} کافی نیست."
            )

            return redirect(
                "cart_detail"
            )


    return render(
        request,
        "cart/checkout.html",
        {
            "cart": cart,
            "address": address,
        }
    )


# =========================================================
# Cancel Cart
# =========================================================

@login_required
@require_POST
def cancel_cart(request):

    cart = Cart.get_active_cart(
        request.user
    )


    if not cart:

        messages.warning(
            request,
            "سبد خرید فعالی وجود ندارد."
        )

        return redirect(
            "cart_detail"
        )


    cart.status = Cart.Status.CANCELLED

    cart.save()


    messages.success(
        request,
        "سبد خرید شما لغو شد."
    )


    return redirect(
        "cart_detail"
    )

def cart_count(request):

    if request.user.is_authenticated:

        cart = Cart.get_active_cart(
            request.user
        )

        count = (
            cart.total_items
            if cart
            else 0
        )

    else:

        count = get_guest_cart_count(
            request
        )


    return JsonResponse(
        {
            "cart_count": count
        }
    )