from apps.payment.models import Payment



def get_payment_stats():


    return {


        # کل تراکنش‌ها
        "total_payments": Payment.objects.count(),



        # پرداخت موفق
        "successful_payments": Payment.objects.filter(
            status=Payment.Status.SUCCESS
        ).count(),



        # پرداخت ناموفق
        "failed_payments": Payment.objects.filter(
            status=Payment.Status.FAILED
        ).count(),



        # در انتظار پرداخت
        "pending_payments": Payment.objects.filter(
            status=Payment.Status.PENDING
        ).count(),



        # لغو شده
        "cancelled_payments": Payment.objects.filter(
            status=Payment.Status.CANCELLED
        ).count(),


    }