
from .models import Product, Order, OrderItem
from .serializers import ProductSerializer, BuySerializer, OrderSerializer
from .permissions import IsAdminOrReadOnly
from django.db import transaction, models
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

class BuyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BuySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        with transaction.atomic():
            product = Product.objects.filter(
                pk=product_id,
                is_active=True,
            ).first()

            if product is None:
                return Response(
                    {"error": "Product not found or inactive."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Deduct stock only if enough stock is available.
            updated = Product.objects.filter(
                pk=product_id,
                is_active=True,
                stock__gte=quantity,
            ).update(
                stock=models.F("stock") - quantity
            )

            if updated == 0:
                return Response(
                    {"error": "Insufficient stock."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            order = Order.objects.create(
                user=request.user,
            )

            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price,
            )

            product.refresh_from_db()

        return Response(
            {
                "message": "Purchase successful.",
                "order_id": order.id,
                "product_id": product.id,
                "product_name": product.name,
                "quantity": order_item.quantity,
                "unit_price": str(order_item.unit_price),
                "subtotal": str(order_item.subtotal),
                "remaining_stock": product.stock,
            },
            status=status.HTTP_201_CREATED,
        )

class MyOrdersAPIView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related("items__product")
            .order_by("-created_at")
        )