from django.urls import path

from .views import (
    RegisterView,
    MeView,
    AdminTestView,
    CategoryPermissionTestView,
    login_view,
    register_view,
    logout_view,
    profile_view,
    address_create_view,
    address_edit_view,
    address_set_default_view,
    address_delete_view,
)


urlpatterns = [

    # =========================================
    # Web
    # =========================================

    path(
        "login/",
        login_view,
        name="login",
    ),

    path(
        "register/",
        register_view,
        name="register",
    ),

    path(
        "logout/",
        logout_view,
        name="logout",
    ),

    path(
        "profile/",
        profile_view,
        name="profile",
    ),


    # =========================================
    # Address Management
    # =========================================

    path(
        "addresses/create/",
        address_create_view,
        name="address_create",
    ),

    path(
        "addresses/<int:address_id>/edit/",
        address_edit_view,
        name="address_edit",
    ),

    path(
        "addresses/<int:address_id>/default/",
        address_set_default_view,
        name="address_set_default",
    ),

    path(
        "addresses/<int:address_id>/delete/",
        address_delete_view,
        name="address_delete",
    ),


    # =========================================
    # API
    # =========================================

    path(
        "api-register/",
        RegisterView.as_view(),
        name="api-register",
    ),

    path(
        "me/",
        MeView.as_view(),
        name="me",
    ),

    path(
        "admin-test/",
        AdminTestView.as_view(),
        name="admin-test",
    ),

    path(
        "category-permission-test/",
        CategoryPermissionTestView.as_view(),
        name="category-permission-test",
    ),

]