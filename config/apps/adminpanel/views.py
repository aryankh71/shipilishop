from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import AdminTokenApprovalForm
from django.contrib.admin.views.decorators import staff_member_required
from .services import approve_admin_request

from .decorators import admin_required
from .models import AdminAccess, AdminRequest
from .services import (
    create_admin_request,
    hash_secret,
    issue_admin_token,
    verify_admin_otp as verify_otp_service,
)


# =========================================================
# Request Admin Access
# =========================================================

@login_required
def request_admin_access(request):

    if request.user.role != request.user.Role.ADMIN:
        return redirect("profile")

    if request.method == "POST":

        try:

            admin_request = create_admin_request(
                request.user
            )

            request.session["admin_request_id"] = (
                admin_request.id
            )

            return redirect(
                "adminpanel:verify_admin_otp"
            )

        except (
            PermissionError,
            ValueError,
        ) as exc:

            return render(
                request,
                "adminpanel/request_access.html",
                {
                    "error": str(exc),
                },
            )

    return render(
        request,
        "adminpanel/request_access.html",
    )


# =========================================================
# Verify OTP
# =========================================================

@login_required
def verify_admin_otp(request):

    if request.user.role != request.user.Role.ADMIN:
        return redirect("profile")

    request_id = request.session.get(
        "admin_request_id"
    )

    if not request_id:
        return redirect(
            "adminpanel:request_admin_access"
        )

    admin_request = get_object_or_404(
        AdminRequest,
        id=request_id,
        user=request.user,
    )

    if request.method == "POST":

        otp = request.POST.get(
            "otp",
            "",
        ).strip()

        if not otp:
            return render(
                request,
                "adminpanel/verify_otp.html",
                {
                    "error": "لطفاً رمز یکبارمصرف را وارد کنید.",
                },
            )

        try:

            verify_otp_service(
                admin_request,
                otp,
            )

            issue_admin_token(
                admin_request
            )

            request.session.pop(
                "admin_request_id",
                None,
            )

            return render(
                request,
                "adminpanel/request_submitted.html",
                {
                    "message": (
                        "رمز یکبارمصرف با موفقیت تأیید شد. "
                        "توکن برای Superuser ارسال شد."
                    ),
                },
            )

        except (
            PermissionError,
            ValueError,
        ) as exc:

            return render(
                request,
                "adminpanel/verify_otp.html",
                {
                    "error": str(exc),
                },
            )

    return render(
        request,
        "adminpanel/verify_otp.html",
    )


# =========================================================
# Dynamic Admin Entry
# =========================================================

def dynamic_admin_entry(request, url_secret):

    url_secret_hash = hash_secret(
        url_secret
    )

    access = (
        AdminAccess.objects
        .filter(
            token_hash=url_secret_hash,
            status=AdminAccess.Status.ACTIVE,
        )
        .select_related("user")
        .first()
    )
    if not access:
        return render(
            request,
            "adminpanel/access_denied.html",
            {
                "error": (
                    "این لینک معتبر نیست یا "
                    "دسترسی آن لغو شده است."
                ),
            },
            status=403,
        )

    user = access.user

    # -----------------------------------------------------
    # Role check
    # -----------------------------------------------------

    if user.role != user.Role.ADMIN:
        return render(
            request,
            "adminpanel/access_denied.html",
            {
                "error": (
                    "نقش این کاربر دیگر ADMIN نیست."
                ),
            },
            status=403,
        )

    # -----------------------------------------------------
    # If another user is already logged in
    # -----------------------------------------------------

    if (
        request.user.is_authenticated
        and request.user.pk != user.pk
    ):
        return render(
            request,
            "adminpanel/access_denied.html",
            {
                "error": (
                    "این لینک متعلق به کاربر دیگری است."
                ),
            },
            status=403,
        )

    # -----------------------------------------------------
    # Login target user
    # -----------------------------------------------------

    if not request.user.is_authenticated:

        login(
            request,
            user,
        )

    return redirect(
        "adminpanel:dashboard"
    )


# =========================================================
# Dashboard
# =========================================================

@admin_required
def dashboard(request):

    return render(
        request,
        "adminpanel/dashboard.html",
        {
            "admin_access": request.admin_access,
        },
    )


# =========================================================
# Admin Logout
# =========================================================

@login_required
def admin_logout(request):

    logout(request)

    return redirect("profile")



@staff_member_required
def approve_admin_access(request, request_id):

    # فقط Superuser
    if not request.user.is_superuser:
        return render(
            request,
            "adminpanel/access_denied.html",
            {
                "error": "فقط Superuser می‌تواند دسترسی Admin را تأیید کند."
            },
            status=403,
        )

    admin_request = get_object_or_404(
        AdminRequest,
        id=request_id,
    )

    if admin_request.status != AdminRequest.Status.TOKEN_ISSUED:
        return render(
            request,
            "adminpanel/access_denied.html",
            {
                "error": "این درخواست در وضعیت قابل تأیید نیست."
            },
            status=400,
        )

    if request.method == "POST":

        form = AdminTokenApprovalForm(
            request.POST
        )

        if form.is_valid():

            token = form.cleaned_data["token"]

            try:

                access, dynamic_url = approve_admin_request(
                    admin_request,
                    token,
                    request.user,
                )

                return render(
                    request,
                    "adminpanel/approval_success.html",
                    {
                        "access": access,
                        "dynamic_url": dynamic_url,
                    },
                )

            except (
                PermissionError,
                ValueError,
            ) as exc:

                form.add_error(
                    "token",
                    str(exc),
                )

    else:

        form = AdminTokenApprovalForm()

    return render(
        request,
        "adminpanel/approve_access.html",
        {
            "form": form,
            "admin_request": admin_request,
        },
    )



def dynamic_admin_entry(request, url_secret):
    url_secret_hash = hash_secret(url_secret)

    print("\n========== DYNAMIC ADMIN DEBUG ==========")
    print("URL SECRET:", url_secret)
    print("URL HASH:", url_secret_hash)

    access = (
        AdminAccess.objects
        .filter(
            url_secret_hash=url_secret_hash,
        )
        .select_related("user")
        .first()
    )

    print("ACCESS:", access)

    if access:
        print("ACCESS ID:", access.id)
        print("ACCESS STATUS:", access.status)
        print("ACCESS USER:", access.user.username)

    print("=========================================\n")

    if not access:
        return render(
            request,
            "adminpanel/access_denied.html",
            {"error": "این لینک معتبر نیست یا دسترسی آن لغو شده است."},
            status=403,
        )

    if access.status != AdminAccess.Status.ACTIVE:
        return render(
            request,
            "adminpanel/access_denied.html",
            {"error": "این دسترسی لغو شده است."},
            status=403,
        )

    user = access.user

    if user.role != user.Role.ADMIN:
        return render(
            request,
            "adminpanel/access_denied.html",
            {"error": "نقش این کاربر دیگر ADMIN نیست."},
            status=403,
        )

    if request.user.is_authenticated and request.user.pk != user.pk:
        return render(
            request,
            "adminpanel/access_denied.html",
            {"error": "این لینک متعلق به کاربر دیگری است."},
            status=403,
        )

    if not request.user.is_authenticated:
        login(request, user)

    return redirect("adminpanel:dashboard")