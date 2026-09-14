from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    message = "شما دسترسی مدیریت ندارید."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.role == "ADMIN"
            )
        )


class CanViewCategory(BasePermission):
    message = "شما اجازه مشاهده دسته‌بندی‌ها را ندارید."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.has_perm("shop.view_category")
        )