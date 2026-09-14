from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.cart_detail,
        name="cart_detail"
    ),


    path(
        "add/<int:variant_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),


    path(
        "increase/<int:item_id>/",
        views.increase_cart_item,
        name="increase_cart_item"
    ),


    path(
        "decrease/<int:item_id>/",
        views.decrease_cart_item,
        name="decrease_cart_item"
    ),


    path(
        "remove/<int:item_id>/",
        views.remove_cart_item,
        name="remove_cart_item"
    ),


    path(
        "cancel/",
        views.cancel_cart,
        name="cancel_cart"
    ),


    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),

    path(
    "count/",
    views.cart_count,
    name="cart_count"
),

]