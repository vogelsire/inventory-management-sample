from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BuyAPIView, MyOrdersAPIView, ProductViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")

urlpatterns = [
    path("buy/", BuyAPIView.as_view(), name="buy"),
    path("my-orders/", MyOrdersAPIView.as_view(), name="my-orders"),
] + router.urls