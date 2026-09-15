from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect, render

from .permissions import IsAdmin, CanViewCategory
from .serializers import RegisterSerializer, UserSerializer

from django.contrib.auth.decorators import login_required
from .models import User, Address, CustomerProfile
from .forms import (
    UserAccountForm,
    CustomerProfileForm,
    AddressForm,
)

from apps.cart.models import Cart,CartItem
from apps.shop.models import ProductVariant
from apps.order.models import Order
from apps.payment.models import Payment



# =========================
# API Register
# =========================

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# =========================
# Web Login
# =========================
def merge_guest_cart(request, user):

    guest_cart = request.session.get(
        "guest_cart",
        {}
    )

    if not guest_cart:
        return


    cart = Cart.get_active_cart(
        user
    )


    if not cart:

        cart = Cart.objects.create(
            user=user,
            status=Cart.Status.ACTIVE
        )


    for variant_id, quantity in guest_cart.items():

        try:

            variant = ProductVariant.objects.get(
                id=int(variant_id)
            )

        except ProductVariant.DoesNotExist:

            continue


        if variant.available_stock <= 0:

            continue


        try:
            quantity = int(quantity)

        except (TypeError, ValueError):
            continue
        
        if quantity <= 0:
            continue

        cart_item = CartItem.objects.filter(
            cart=cart,
            variant=variant
        ).first()


        if cart_item:

            new_quantity = (
                cart_item.quantity
                + quantity
            )

            cart_item.quantity = min(
                new_quantity,
                variant.available_stock
            )

            cart_item.save()


        else:

            CartItem.objects.create(
                cart=cart,
                variant=variant,
                quantity=min(
                    quantity,
                    variant.available_stock
                )
            )


    request.session.pop(
        "guest_cart",
        None
    )

    request.session.modified = True

    
def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    next_url = (
        request.GET.get("next")
        or request.POST.get("next")
    )
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(request, user)

            merge_guest_cart(
                request,
                user
            )

            messages.success(
                request,
                "با موفقیت وارد شدید."
            )

            if next_url:
                return redirect(next_url)

            return redirect("home")

        messages.error(
            request,
            "نام کاربری یا رمز عبور اشتباه است."
        )

    return render(
        request,
        "account/login.html",
        {
            "next": next_url,
            }
    )


# =========================
# Web Register
# =========================

def register_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    next_url = (
        request.GET.get("next")
        or request.POST.get("next")
    )

    if next_url in ["None", ""]:
        
        next_url = None

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        email = request.POST.get(
            "email"
        )

        password = request.POST.get(
            "password"
        )

        password2 = request.POST.get(
            "password2"
        )


        # بررسی خالی نبودن فیلدها

        if not username or not email or not password:

            messages.error(
                request,
                "لطفاً تمام اطلاعات را وارد کنید."
            )

            return render(
                request,
                "account/register.html",
                {
                    "next": next_url,
                }
            )


        # بررسی یکسان بودن رمز عبور

        if password != password2:

            messages.error(
                request,
                "رمز عبور و تکرار آن یکسان نیست."
            )

            return render(
                request,
                "account/register.html",
                {
                    "next": next_url,
                }
            )



        # بررسی تکراری نبودن Username

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "این نام کاربری قبلاً ثبت شده است."
            )

            return render(
                request,
                "account/register.html",
                {
                    "next":next_url,
                    }
            )


        # بررسی تکراری نبودن Email

        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "این ایمیل قبلاً ثبت شده است."
            )

            return render(
                request,
                "account/register.html",
                {
                    "next":next_url,
                }
            )


        # ایجاد کاربر

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )


        # ورود خودکار بعد از ثبت نام

        login(
            request,
            user
        )

        merge_guest_cart(
            request,
            user
        )


        messages.success(
            request,
            "ثبت نام با موفقیت انجام شد."
        )

        if next_url:

            return redirect(
                next_url
            )


        return redirect(
            "home"
        )


    return render(
        request,
        "account/register.html",
        {
            "next": next_url,
            }
    )



# =========================
# Web Logout
# =========================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "با موفقیت از حساب خارج شدید."
    )

    return redirect("home")


# =========================
# API Me
# =========================

class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserSerializer(
            request.user
        )

        return Response(
            serializer.data
        )


# =========================
# API Admin Test
# =========================

class AdminTestView(APIView):

    permission_classes = [IsAdmin]

    def get(self, request):

        return Response({
            "message": "شما به بخش مدیریت دسترسی دارید."
        })


# =========================
# API Category Permission
# =========================

class CategoryPermissionTestView(APIView):

    permission_classes = [CanViewCategory]

    def get(self, request):

        return Response({
            "message": "شما Permission مشاهده دسته‌بندی را دارید."
        })
@login_required
def profile_view(request):


    # =========================================
    # Customer Profile
    # =========================================

    profile, created = CustomerProfile.objects.get_or_create(
        user=request.user
    )


    # =========================================
    # User Addresses
    # =========================================

    addresses = Address.objects.filter(
        user=request.user
    ).order_by(
        "-is_default",
        "-updated_at"
    )


    default_address = addresses.filter(
        is_default=True
    ).first()


    # =========================================
    # User Orders
    # =========================================

    orders = (
        Order.objects
        .filter(
            user=request.user
        )
        # .prefetch_related(
        #     Prefetch(
        #         "payments",
        #         queryset=Payment.objects.order_by(
        #             "-created_at"
        #         ),
        #         to_attr="ordered_payments"
        #     ),
        #     "items__variant"
        # )
        .order_by(
            "-created_at"
        )
    )


    # =========================================
    # Latest Payment For Each Order
    # =========================================

    # for order in orders:

    #     order.latest_payment = (
    #         order.ordered_payments[0]
    #         if order.ordered_payments
    #         else None
    #     )


    # =========================================
    # Account Form
    # =========================================

    account_form = UserAccountForm(
        instance=request.user
    )


    # =========================================
    # Personal Profile Form
    # =========================================

    profile_form = CustomerProfileForm(
        instance=profile
    )


    # =========================================
    # Create Address Form
    # =========================================

    address_form = AddressForm()


    # =========================================
    # Edit Address
    # =========================================

    edit_address = None

    edit_address_form = None


    edit_address_id = request.GET.get(
        "edit_address"
    )


    if edit_address_id:

        edit_address = get_object_or_404(
            Address,
            id=edit_address_id,
            user=request.user
        )


        edit_address_form = AddressForm(
            instance=edit_address
        )


    # =========================================
    # POST
    # =========================================

    if request.method == "POST":

        form_type = request.POST.get(
            "form_type"
        )


        # =====================================
        # Account Form
        # =====================================

        if form_type == "account":

            account_form = UserAccountForm(
                request.POST,
                instance=request.user
            )


            if account_form.is_valid():

                account_form.save()


                messages.success(
                    request,
                    "اطلاعات حساب کاربری با موفقیت بروزرسانی شد."
                )


                return redirect(
                    "profile"
                )


        # =====================================
        # Personal Profile Form
        # =====================================

        elif form_type == "personal":

            profile_form = CustomerProfileForm(
                request.POST,
                request.FILES,
                instance=profile
            )


            if profile_form.is_valid():

                profile_form.save()


                messages.success(
                    request,
                    "اطلاعات شخصی با موفقیت بروزرسانی شد."
                )


                return redirect(
                    "profile"
                )


        # =====================================
        # Create Address
        # =====================================

        elif form_type == "address":

            address_form = AddressForm(
                request.POST
            )


            if address_form.is_valid():

                address = address_form.save(
                    commit=False
                )


                address.user = request.user


                # First address becomes default

                if not addresses.exists():

                    address.is_default = True


                address.save()


                messages.success(
                    request,
                    "آدرس جدید با موفقیت ثبت شد."
                )


                return redirect(
                    "profile"
                )


        # =====================================
        # Edit Address
        # =====================================

        elif form_type == "edit_address":

            address_id = request.POST.get(
                "address_id"
            )


            edit_address = get_object_or_404(
                Address,
                id=address_id,
                user=request.user
            )


            edit_address_form = AddressForm(
                request.POST,
                instance=edit_address
            )


            if edit_address_form.is_valid():

                edit_address_form.save()


                messages.success(
                    request,
                    "آدرس با موفقیت بروزرسانی شد."
                )


                return redirect(
                    "profile"
                )


    # =========================================
    # Render
    # =========================================

    return render(
        request,
        "account/profile.html",
        {

            "account_form": account_form,

            "profile_form": profile_form,

            "profile": profile,

            "addresses": addresses,

            "default_address": default_address,

            "address_form": address_form,

            "edit_address": edit_address,

            "edit_address_form": edit_address_form,

            "orders": orders,

        }
    )

    
@login_required
def address_list_view(request):
    addresses = Address.objects.filter(
        user=request.user
    ).order_by(
        "-is_default",
        "-updated_at"
    )

    return render(
        request,
        "account/address_list.html",
        {
            "addresses": addresses,
        }
    )


@login_required
def address_create_view(request):
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            if not Address.objects.filter(user=request.user).exists():
                address.is_default = True

            address.save()

            messages.success(
                request,
                "آدرس با موفقیت ثبت شد."
            )

            if next_url:
                return redirect(next_url)

            return redirect("profile")

    else:
        form = AddressForm()

    return render(
        request,
        "account/address_form.html",
        {
            "form": form,
            "page_title": "افزودن آدرس جدید",
            "next": next_url,
        }
    )


@login_required
def address_edit_view(request, address_id):
    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        form = AddressForm(
            request.POST,
            instance=address
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "آدرس با موفقیت بروزرسانی شد."
            )

            if next_url:
                return redirect(next_url)

            return redirect("profile")

    else:
        form = AddressForm(instance=address)

    return render(
        request,
        "account/address_form.html",
        {
            "form": form,
            "address": address,
            "page_title": "ویرایش آدرس",
            "next": next_url,
        }
    )


@login_required
def address_set_default_view(request, address_id):


    if request.method != "POST":

        return redirect(
            "profile"
        )


    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )


    address.is_default = True


    address.save()


    messages.success(
        request,
        "آدرس پیش‌فرض با موفقیت تغییر کرد."
    )


    return redirect(
        "profile"
    )


@login_required
def address_delete_view(request, address_id):


    if request.method != "POST":

        return redirect(
            "profile"
        )


    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )


    was_default = address.is_default


    address.delete()


    # اگر آدرس پیش‌فرض حذف شد،
    # آخرین آدرس باقی‌مانده پیش‌فرض شود.

    if was_default:

        new_default = Address.objects.filter(
            user=request.user
        ).order_by(
            "-updated_at"
        ).first()


        if new_default:

            new_default.is_default = True

            new_default.save()


    messages.success(
        request,
        "آدرس با موفقیت حذف شد."
    )


    return redirect(
        "profile"
    )