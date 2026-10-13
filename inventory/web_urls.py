from django.contrib.auth import views as auth_views
from django.urls import path

from . import web_views

urlpatterns = [
    path("", web_views.store, name="store"),
    path("my-orders/", web_views.my_orders, name="my-orders"),
    path(
        "buy/<int:product_id>/",
        web_views.buy_product,
        name="buy-product",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="/"),
        name="logout",
    ),
    path(
        "inventory/",
        web_views.inventory_dashboard,
        name="inventory-dashboard",
    ),
    path(
        "inventory/add/",
        web_views.product_create,
        name="product-create",
    ),
    path(
        "inventory/<int:product_id>/edit/",
        web_views.product_edit,
        name="product-edit",
    ),
    path(
        "inventory/<int:product_id>/delete/",
        web_views.product_delete,
        name="product-delete",
    ),
    path(
        "my-orders/",
        web_views.my_orders,
        name="web-my-orders",
    ),
]