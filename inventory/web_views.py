from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProductForm
from .models import Order, OrderItem, Product

def store(request):
    products = Product.objects.filter(
        is_active=True
    ).order_by("name")

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(name__icontains=query)

    return render(request, "inventory/product_list.html", {
        "products": products,
        "query": query,
    })


@login_required
def my_orders(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )

    return render(request, "inventory/my_orders.html", {
        "orders": orders,
    })


@login_required
@require_POST
def buy_product(request, product_id):
    try:
        quantity = int(request.POST.get("quantity", "1"))
        if quantity < 1:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, "Please enter a valid quantity.")
        return redirect("store")

    with transaction.atomic():
        product = get_object_or_404(
            Product,
            pk=product_id,
            is_active=True,
        )

        updated = Product.objects.filter(
            pk=product_id,
            is_active=True,
            stock__gte=quantity,
        ).update(stock=F("stock") - quantity)

        if updated == 0:
            messages.error(
                request,
                "Purchase failed. There may not be enough stock.",
            )
            return redirect("store")

        order = Order.objects.create(user=request.user)

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=product.price,
        )

    messages.success(
        request,
        f"Purchase successful! Order #{order.id} has been created.",
    )
    return redirect("my-orders")


@staff_member_required(login_url="login")
def inventory_dashboard(request):
    products = Product.objects.all().order_by("name")

    return render(request, "inventory/inventory_dashboard.html", {
        "products": products,
        "total_products": products.count(),
        "active_products": products.filter(is_active=True).count(),
        "low_stock_products": products.filter(stock__lte=5).count(),
    })


@staff_member_required(login_url="login")
def product_create(request):
    form = ProductForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Product created successfully.")
        return redirect("inventory-dashboard")

    return render(request, "inventory/product_form.html", {
        "form": form,
        "page_title": "Add Product",
    })


@staff_member_required(login_url="login")
def product_edit(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    form = ProductForm(request.POST or None, instance=product)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Product updated successfully.")
        return redirect("inventory-dashboard")

    return render(request, "inventory/product_form.html", {
        "form": form,
        "page_title": "Edit Product",
    })


@staff_member_required(login_url="login")
def product_delete(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == "POST":
        # Prevent deletion if this product appears in an order.
        if product.order_items.exists():
            messages.error(
                request,
                "This product has order history and cannot be deleted. "
                "You can deactivate it instead.",
            )
        else:
            product.delete()
            messages.success(request, "Product deleted successfully.")

        return redirect("inventory-dashboard")

    return render(request, "inventory/product_confirm_delete.html", {
        "product": product,
    })
