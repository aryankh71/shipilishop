import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from .models import AdminAccess, AdminOTP, AdminRequest


User = get_user_model()


OTP_EXPIRY_MINUTES = 5
OTP_MAX_ATTEMPTS = 5


# =========================================================
# Security Helpers
# =========================================================

def hash_secret(value):
    return hashlib.sha512(
        value.encode("utf-8")
    ).hexdigest()


def generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def generate_admin_token():
    return secrets.token_urlsafe(48)


def generate_url_secret():
    """
    Secret used only inside the Dynamic Admin URL.
    """

    return secrets.token_urlsafe(48)


def build_dynamic_admin_url(url_secret):
    """
    Build Dynamic Admin URL using the URL secret.

    The Admin Token is NEVER placed inside the URL.
    """

    path = reverse(
        "adminpanel:dynamic_admin_entry",
        kwargs={
            "url_secret": url_secret,
        },
    )

    base_url = getattr(
        settings,
        "SITE_BASE_URL",
        "",
    ).rstrip("/")

    return f"{base_url}{path}"


# =========================================================
# Admin Request
# =========================================================

@transaction.atomic
def create_admin_request(user):

    if user.role != user.Role.ADMIN:
        raise PermissionError(
            "فقط کاربران دارای نقش ADMIN می‌توانند درخواست دسترسی ادمین بدهند."
        )

    active_access = AdminAccess.objects.filter(
        user=user,
        status=AdminAccess.Status.ACTIVE,
    ).exists()

    if active_access:
        raise ValueError(
            "این کاربر در حال حاضر دسترسی فعال ادمین دارد."
        )

    unfinished_request = AdminRequest.objects.filter(
        user=user,
        status__in=[
            AdminRequest.Status.PENDING_OTP,
            AdminRequest.Status.OTP_VERIFIED,
            AdminRequest.Status.TOKEN_ISSUED,
        ],
    ).exists()

    if unfinished_request:
        raise ValueError(
            "برای این کاربر یک درخواست فعال وجود دارد."
        )

    if not user.email:
        raise ValueError(
            "برای این کاربر ایمیل ثبت نشده است."
        )

    admin_request = AdminRequest.objects.create(
        user=user,
        status=AdminRequest.Status.PENDING_OTP,
    )

    otp = generate_otp()

    AdminOTP.objects.create(
        request=admin_request,
        otp_hash=hash_secret(otp),
        expires_at=(
            timezone.now()
            + timedelta(minutes=OTP_EXPIRY_MINUTES)
        ),
    )

    print(
        f"ADMIN OTP for{admin_request.user.username}: {otp}"
          )

    return admin_request


# =========================================================
# OTP Verification
# =========================================================

@transaction.atomic
def verify_admin_otp(admin_request, otp):

    user = admin_request.user

    if user.role != user.Role.ADMIN:
        raise PermissionError(
            "کاربر دیگر مجوز ADMIN ندارد."
        )

    if admin_request.status != AdminRequest.Status.PENDING_OTP:
        raise ValueError(
            "این درخواست در وضعیت انتظار برای OTP نیست."
        )

    otp_record = (
        admin_request.otps
        .filter(
            verified_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )

    if not otp_record:
        raise ValueError(
            "OTP معتبری برای این درخواست وجود ندارد."
        )

    if timezone.now() >= otp_record.expires_at:
        raise ValueError(
            "OTP منقضی شده است."
        )

    if otp_record.attempts >= OTP_MAX_ATTEMPTS:
        raise ValueError(
            "تعداد تلاش‌های مجاز برای OTP تمام شده است."
        )

    otp_record.attempts += 1

    otp_record.save(
        update_fields=["attempts"]
    )

    if not secrets.compare_digest(
        hash_secret(otp),
        otp_record.otp_hash,
    ):
        raise ValueError(
            "OTP اشتباه است."
        )

    otp_record.verified_at = timezone.now()

    otp_record.save(
        update_fields=["verified_at"]
    )

    admin_request.status = AdminRequest.Status.OTP_VERIFIED

    admin_request.save(
        update_fields=["status"]
    )

    return admin_request


# =========================================================
# Token Issuance
# =========================================================

@transaction.atomic
def issue_admin_token(admin_request):

    user = admin_request.user

    if user.role != user.Role.ADMIN:
        raise PermissionError(
            "کاربر دیگر ADMIN نیست."
        )

    if admin_request.status != AdminRequest.Status.OTP_VERIFIED:
        raise ValueError(
            "این درخواست هنوز OTP را با موفقیت تأیید نکرده است."
        )

    token = generate_admin_token()

    admin_request.token_hash = hash_secret(token)

    admin_request.token_issued_at = timezone.now()

    admin_request.status = AdminRequest.Status.TOKEN_ISSUED

    admin_request.save(
        update_fields=[
            "token_hash",
            "token_issued_at",
            "status",
        ]
    )

    notify_superuser_about_token(
        admin_request=admin_request,
        token=token,
    )

    return token


# =========================================================
# Superuser Notification
# =========================================================

def notify_superuser_about_token(
    admin_request,
    token,
):

    superusers = (
        User.objects
        .filter(
            is_superuser=True,
            is_active=True,
        )
        .exclude(
            email__isnull=True,
        )
        .exclude(
            email="",
        )
    )

    recipient_list = list(
        superusers.values_list(
            "email",
            flat=True,
        )
    )

    if not recipient_list:
        return

    user = admin_request.user

    send_mail(
        subject="درخواست فعال‌سازی دسترسی Admin",
        message=(
            "یک کاربر درخواست فعال‌سازی دسترسی Admin داده است.\n\n"
            "مشخصات کاربر:\n"
            "-------------------------\n"
            f"Username: {user.username}\n"
            f"Name: {user.get_full_name()}\n"
            f"Email: {user.email}\n"
            f"Phone: {user.phone_number}\n\n"
            "Admin Token:\n"
            "-------------------------\n"
            f"{token}\n\n"
            "این Token را در Django Admin بررسی و تأیید کنید.\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )


# =========================================================
# Approve Admin Request
# =========================================================

@transaction.atomic
def approve_admin_request(
    admin_request,
    token,
    approving_user,
):

    if not approving_user.is_authenticated:
        raise PermissionError(
            "برای تأیید دسترسی باید وارد حساب شوید."
        )

    if not approving_user.is_superuser:
        raise PermissionError(
            "فقط Superuser می‌تواند درخواست Admin را تأیید کند."
        )

    user = admin_request.user

    if user.role != user.Role.ADMIN:
        raise PermissionError(
            "این کاربر دیگر نقش ADMIN ندارد."
        )

    if admin_request.status != AdminRequest.Status.TOKEN_ISSUED:
        raise ValueError(
            "این درخواست در وضعیت قابل تأیید نیست."
        )

    if not admin_request.token_hash:
        raise ValueError(
            "Token برای این درخواست وجود ندارد."
        )

    if not secrets.compare_digest(
        hash_secret(token),
        admin_request.token_hash,
    ):
        raise ValueError(
            "Token اشتباه است."
        )

    active_access = AdminAccess.objects.filter(
        user=user,
        status=AdminAccess.Status.ACTIVE,
    ).exists()

    if active_access:
        raise ValueError(
            "این User قبلاً دسترسی فعال دارد."
        )

    # -----------------------------------------------------
    # Generate a completely separate URL secret
    # -----------------------------------------------------

    url_secret = generate_url_secret()

    access = AdminAccess.objects.create(
        request=admin_request,
        user=user,
        token_hash=admin_request.token_hash,
        url_secret_hash=hash_secret(url_secret),
        status=AdminAccess.Status.ACTIVE,
    )

    admin_request.status = AdminRequest.Status.APPROVED

    admin_request.approved_at = timezone.now()

    admin_request.save(
        update_fields=[
            "status",
            "approved_at",
        ]
    )

    dynamic_url = build_dynamic_admin_url(
        url_secret
    )

    return access, dynamic_url


# =========================================================
# Revoke Admin Access
# =========================================================

@transaction.atomic
def revoke_admin_access(
    access,
    revoking_user,
):

    if not revoking_user.is_authenticated:
        raise PermissionError(
            "برای لغو دسترسی باید وارد حساب شوید."
        )

    if not revoking_user.is_superuser:
        raise PermissionError(
            "فقط Superuser می‌تواند دسترسی Admin را لغو کند."
        )

    if access.status == AdminAccess.Status.REVOKED:
        raise ValueError(
            "این دسترسی قبلاً لغو شده است."
        )

    access.status = AdminAccess.Status.REVOKED

    access.revoked_at = timezone.now()

    access.save(
        update_fields=[
            "status",
            "revoked_at",
        ]
    )

    return access