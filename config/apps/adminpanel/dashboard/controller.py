from django.shortcuts import render

from ..decorators import admin_required

from .modules.products import get_product_stats
from .modules.payments import get_payment_stats
from .modules.orders import (
    get_order_stats,
    get_latest_orders
)


@admin_required
def dashboard(request):
    print("DASHBOARD VIEW RUNNING")


    context = {

        "admin_access": request.admin_access,


        **get_product_stats(),


        **get_order_stats(),


        **get_payment_stats(),


        "latest_orders": get_latest_orders(),

    }


    print("khorooji=====>",context)
    return render(
        request,
        "adminpanel/dashboard.html",
        context
    )