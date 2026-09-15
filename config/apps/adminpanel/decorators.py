from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from .models import AdminAccess


def admin_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # ---------------------------------------------
        # 1. User must be authenticated
        # ---------------------------------------------

        if not request.user.is_authenticated:
            return redirect_to_login(
                request.get_full_path()
            )

        # ---------------------------------------------
        # 2. User must still be ADMIN
        # ---------------------------------------------

        if request.user.role != request.user.Role.ADMIN:
            return redirect("profile")

        # ---------------------------------------------
        # 3. User must have an ACTIVE AdminAccess
        # ---------------------------------------------

        access = (
            AdminAccess.objects
            .filter(
                user=request.user,
                status=AdminAccess.Status.ACTIVE,
            )
            .order_by("-created_at")
            .first()
        )

        if not access:
            return redirect("profile")

        # ---------------------------------------------
        # 4. Make access available to the view
        # ---------------------------------------------

        request.admin_access = access

        return view_func(
            request,
            *args,
            **kwargs,
        )

    return wrapper