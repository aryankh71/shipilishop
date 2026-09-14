from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404, render
from apps.cart.models import Cart
from .models import Order, OrderItem
from apps.shop.models import ProductVariant



@login_required
def create_order(request):

    # فقط درخواست POST مجاز باشد
    if request.method != "POST":

        return redirect(
            "cart_detail"
        )


    # گرفتن Cart فعال
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


    # بررسی انقضا
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


    # بررسی خالی نبودن
    if not cart.items.exists():

        messages.warning(
            request,
            "سبد خرید شما خالی است."
        )

        return redirect(
            "cart_detail"
        )



    # گرفتن آدرس پیش فرض
    address = request.user.addresses.filter(
        is_default=True
    ).first()



    if not address or not address.is_complete:

        messages.warning(
            request,
            "لطفاً ابتدا آدرس ارسال را تکمیل کنید."
        )

        return redirect(
            "address_create"
        )



    with transaction.atomic():


        # گرفتن آیتم های سبد
        cart_items = list(
            cart.items.select_related(
                "variant"
            )
        )


        # هماهنگ کردن قیمت با قیمت فعلی محصول
        for cart_item in cart_items:


            current_price = cart_item.variant.price


            if cart_item.unit_price != current_price:


                cart_item.unit_price = current_price


                cart_item.save(
                    update_fields=[
                        "unit_price",
                        "updated_at"
                    ]
                )



        # =================================================
        # اگر برای این Cart سفارش Pending وجود دارد
        # همان سفارش را برگردان
        # =================================================


        existing_order = getattr(
            cart,
            "order",
            None
        )


        if existing_order:


            if existing_order.status == Order.Status.PENDING_PAYMENT:


                return redirect(
                    "order_detail",
                    order_id=existing_order.id
                )



        # =================================================
        # ساخت Order جدید
        # =================================================


        order = Order.objects.create(

            user=request.user,

            cart=cart,

            address=address,

            status=Order.Status.PENDING_PAYMENT
        )



        # =================================================
        # انتقال CartItem به OrderItem
        # =================================================


        for cart_item in cart_items:


            # کنترل موجودی

            if (
                cart_item.quantity
                > cart_item.variant.available_stock
            ):


                messages.error(
                    request,
                    f"موجودی {cart_item.variant} کافی نیست."
                )


                transaction.set_rollback(
                    True
                )


                return redirect(
                    "cart_detail"
                )



            OrderItem.objects.create(

                order=order,

                variant=cart_item.variant,

                quantity=cart_item.quantity,

                unit_price=cart_item.unit_price

            )



        # =================================================
        # تغییر وضعیت Cart
        # =================================================


        cart.status = Cart.Status.CHECKOUT

        cart.save()



    messages.success(
        request,
        "سفارش شما با موفقیت ایجاد شد."
    )



    return redirect(
        "order_detail",
        order_id=order.id
    )
# @login_required
# def create_order(request):

#     # فقط درخواست POST مجاز باشد
#     if request.method != "POST":

#         return redirect(
#             "cart_detail"
#         )


#     # گرفتن Cart فعال
#     cart = Cart.get_active_cart(
#         request.user
#     )


#     # بررسی وجود Cart
#     if not cart:

#         messages.warning(
#             request,
#             "سبد خرید فعالی وجود ندارد."
#         )

#         return redirect(
#             "cart_detail"
#         )


#     # بررسی منقضی شدن Cart
#     if cart.is_expired:

#         cart.status = Cart.Status.EXPIRED
#         cart.save()

#         messages.warning(
#             request,
#             "سبد خرید شما منقضی شده است."
#         )

#         return redirect(
#             "cart_detail"
#         )


#     # بررسی خالی نبودن Cart
#     if not cart.items.exists():

#         messages.warning(
#             request,
#             "سبد خرید شما خالی است."
#         )

#         return redirect(
#             "cart_detail"
#         )


#     # گرفتن آدرس پیش‌فرض کاربر
#     address = request.user.addresses.filter(
#         is_default=True
#     ).first()


#     # بررسی آدرس
#     if not address or not address.is_complete:

#         messages.warning(
#             request,
#             "لطفاً ابتدا آدرس ارسال را تکمیل کنید."
#         )

#         return redirect(
#             "address_create"
#         )


#     # ساخت Order و OrderItemها به صورت اتمیک
#     with transaction.atomic():

#         # ایجاد سفارش
#         order = Order.objects.create(

#             user=request.user,

#             address=address,

#             status=Order.Status.PENDING_PAYMENT
#         )


#         # انتقال CartItem ها به OrderItem
#         for cart_item in cart.items.select_related(
#             "variant"
#         ):

#             OrderItem.objects.create(

#                 order=order,

#                 variant=cart_item.variant,

#                 quantity=cart_item.quantity,

#                 unit_price=cart_item.unit_price
#             )


#         # تغییر وضعیت Cart
#         cart.status = Cart.Status.CHECKOUT

#         cart.save()


#     messages.success(
#         request,
#         "سفارش شما با موفقیت ایجاد شد."
#     )


#     # فعلاً بعد از ایجاد سفارش
#     # به صفحه جزئیات سفارش می‌رویم
#     return redirect(
#         "order_detail",
#         order_id=order.id
#     )




@login_required
def order_detail(request, order_id):

    order = get_object_or_404(

        Order.objects.prefetch_related(
            "items__variant"
        ),

        id=order_id,

        user=request.user
    )


    return render(

        request,

        "order/order_detail.html",

        {
            "order": order
        }
    )