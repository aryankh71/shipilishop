from django.conf import settings

from django.contrib import messages

from django.contrib.auth.decorators import login_required

from django.shortcuts import (
    get_object_or_404,
    redirect,
)

from django.views.decorators.http import require_POST


from apps.order.models import Order

from .models import Payment



# =========================================
# Start Payment
# =========================================

@login_required
@require_POST
def start_payment(
    request,
    order_id
):

    # =====================================
    # Get Order
    # =====================================

    order = get_object_or_404(

        Order,

        id=order_id,

        user=request.user

    )


    # =====================================
    # Check Order Status
    # =====================================

    if (
        order.status
        != Order.Status.PENDING_PAYMENT
    ):

        messages.error(

            request,

            "این سفارش در حال حاضر قابل پرداخت نیست."

        )

        return redirect(

            "order_detail",

            order_id=order.id

        )


    # =====================================
    # Get Existing Payment
    # =====================================

    try:

        payment = order.payment

    except Payment.DoesNotExist:

        payment = Payment.objects.create(

            order=order,

            provider=(
                Payment.Provider.ZARINPAL
            ),

            amount=order.total_price,

            status=(
                Payment.Status.CREATED
            ),

        )


    # =====================================
    # Already Successful Payment
    # =====================================

    if (
        payment.status
        == Payment.Status.SUCCESS
    ):

        messages.success(

            request,

            "این سفارش قبلاً پرداخت شده است."

        )

        return redirect(

            "order_detail",

            order_id=order.id

        )


    # =====================================
    # Retry Failed Payment
    # =====================================

    if (
        payment.status
        == Payment.Status.FAILED
    ):

        payment.status = (
            Payment.Status.CREATED
        )

        payment.failure_reason = None

        payment.gateway_response = None

        payment.authority = None

        payment.reference_id = None

        payment.amount = order.total_price

        payment.save(

            update_fields=[

                "status",

                "failure_reason",

                "gateway_response",

                "authority",

                "reference_id",

                "amount",

                "updated_at",

            ]

        )


    # =====================================
    # Payment Gateway
    # =====================================

    if settings.PAYMENT_GATEWAY_ENABLED:


        # =================================
        # Real Gateway
        # =================================

        """
        مراحل آینده زرین پال:

        1- ارسال payment.amount
        2- دریافت Authority
        3- ذخیره Authority
        4- تغییر وضعیت به PENDING
        5- Redirect به درگاه
        """


        payment.status = (
            Payment.Status.PENDING
        )

        payment.save(

            update_fields=[

                "status",

                "updated_at"

            ]

        )


        return redirect(

            "fake_gateway",

            payment_id=payment.id

        )


    else:


        # =================================
        # Gateway Disabled / Fake Failure
        # =================================

        payment.status = (
            Payment.Status.FAILED
        )

        payment.failure_reason = (
            "درگاه پرداخت در حال حاضر "
            "فعال یا در دسترس نیست."
        )

        payment.save(

            update_fields=[

                "status",

                "failure_reason",

                "updated_at",

            ]

        )


        messages.error(

            request,

            "پرداخت انجام نشد. "

            "درگاه پرداخت در حال حاضر فعال نیست. "

            "لطفاً بعداً دوباره تلاش کنید."

        )


        return redirect(

            "order_detail",

            order_id=order.id

        )