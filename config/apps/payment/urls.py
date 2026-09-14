from django.urls import path

from . import views


app_name = "payment"


urlpatterns = [

    path(
        "start/<int:order_id>/",
        views.start_payment,
        name="start_payment"
    ),

]