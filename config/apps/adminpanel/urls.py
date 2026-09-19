from django.urls import path
from . import views


app_name = "adminpanel"


urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "request/",
        views.request_admin_access,
        name="request_admin_access",
    ),

    path(
        "request/verify/",
        views.verify_admin_otp,
        name="verify_admin_otp",
    ),

    path(
        "access/<str:url_secret>/",
        views.dynamic_admin_entry,
        name="dynamic_admin_entry",
    ),

    path(
    "approve/<int:request_id>/",
    views.approve_admin_access,
    name="approve_admin_access",
    ),

    path(
        "logout/",
        views.admin_logout,
        name="admin_logout",
    ),

    path(
    "products/",
    views.product_list,
    name="products"
    ),


    path(
    "products/<int:product_id>/edit/",
    views.product_edit,
    name="product_edit"
    ),

]