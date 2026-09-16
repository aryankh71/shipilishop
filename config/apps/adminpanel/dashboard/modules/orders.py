from django.db.models import Sum
from django.utils import timezone

from apps.order.models import Order



def get_order_stats():

    today = timezone.localdate()


    return {


        # کل سفارش‌ها
        "total_orders": Order.objects.count(),



        # سفارش‌های امروز
        "today_orders": Order.objects.filter(
            created_at__date=today
        ).count(),



        # در انتظار پرداخت
        "pending_orders": Order.objects.filter(
            status=Order.Status.PENDING_PAYMENT
        ).count(),



        # پرداخت شده
        "paid_orders": Order.objects.filter(
            status=Order.Status.PAID
        ).count(),



        # لغو شده
        "cancelled_orders": Order.objects.filter(
            status=Order.Status.CANCELLED
        ).count(),



        # مبلغ کل فروش
        "total_sales": Order.objects.filter(
            status=Order.Status.PAID
        ).aggregate(
            total=Sum(
                "items__unit_price"
            )
        )["total"] or 0,


    }





def get_latest_orders(limit=5):

    return Order.objects.select_related(
        "user",
        "address"
    ).prefetch_related(
        "items"
    ).order_by(
        "-created_at"
    )[:limit]