from django.urls import path

from apps.adminpanel.dashboard.controllers.products import product_release_lock
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


    # -------------------------------------------------
    # Products
    # -------------------------------------------------

    path(
        "products/",
        views.product_list,
        name="products"
    ),

    path(
        "products/create/",
        views.product_create,
        name="product_create"
    ),

    path(
        "products/<int:product_id>/edit/",
        views.product_edit,
        name="product_edit"
    ),

    path(
        "products/<int:product_id>/delete/",
        views.product_delete,
        name="product_delete"
    ),


    # -------------------------------------------------
    # Categories
    # -------------------------------------------------

    path(
        "categories/",
        views.category_list,
        name="category_list"
    ),

    path(
        "categories/create/",
        views.category_create,
        name="category_create"
    ),

    path(
        "categories/<int:pk>/edit/",
        views.category_update,
        name="category_update"
    ),

    path(
        "categories/<int:pk>/delete/",
        views.category_delete,
        name="category_delete"
    ),

    path(
        "products/<int:product_id>/release-lock/",
        product_release_lock,
        name="product_release_lock",
        ),

]