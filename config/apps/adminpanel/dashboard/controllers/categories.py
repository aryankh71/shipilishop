from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from apps.shop.models import Category

from ...decorators import admin_required
from ...forms import CategoryForm


@admin_required
def category_list(request):

    categories = (
        Category.objects
        .select_related(
            "created_by",
            "updated_by",
        )
        .annotate(
            product_count=Count("products")
        )
        .order_by("name")
    )

    return render(
        request,
        "adminpanel/categories/list.html",
        {
            "categories": categories,
        }
    )


@admin_required
def category_create(request):

    if request.method == "POST":

        form = CategoryForm(request.POST)

        if form.is_valid():

            category = form.save(commit=False)

            category.created_by = request.user
            category.updated_by = request.user

            category.save()

            messages.success(
                request,
                "دسته‌بندی با موفقیت ایجاد شد."
            )

            return redirect(
                "adminpanel:category_list"
            )

    else:

        form = CategoryForm()

    return render(
        request,
        "adminpanel/categories/form.html",
        {
            "form": form,
            "page_title": "افزودن دسته‌بندی",
        }
    )


@admin_required
def category_update(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk
    )

    if request.method == "POST":

        form = CategoryForm(
            request.POST,
            instance=category
        )

        if form.is_valid():

            category = form.save(commit=False)
            category.updated_by = request.user
            category.save()

            messages.success(
                request,
                "دسته‌بندی با موفقیت ویرایش شد."
            )

            return redirect(
                "adminpanel:category_list"
            )

    else:

        form = CategoryForm(
            instance=category
        )

    return render(
        request,
        "adminpanel/categories/form.html",
        {
            "form": form,
            "category": category,
            "page_title": "ویرایش دسته‌بندی",
        }
    )

@admin_required
def category_delete(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk
    )

    if request.method == "POST":

        if category.products.filter(
            is_active=True
        ).exists():

            messages.error(
                request,
                "این دسته‌بندی دارای محصول فعال است و قابل حذف نیست."
            )

            return redirect(
                "adminpanel:category_list"
            )

        category.delete()

        messages.success(
            request,
            "دسته‌بندی با موفقیت حذف شد."
        )

        return redirect(
            "adminpanel:category_list"
        )

    return render(
        request,
        "adminpanel/categories/confirm_delete.html",
        {
            "category": category,
        }
    )