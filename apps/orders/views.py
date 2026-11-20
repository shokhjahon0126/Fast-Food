from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.orders.models import Order
from apps.users.permissions import IsAdminOrCashier
from apps.orders.selectors import get_customer_orders_queryset, get_cashier_orders_queryset
from apps.orders.services import order_accept, order_complete, order_cancel
from apps.orders.filters import OrderFilter
from apps.orders.serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderCancelSerializer,
)


class CustomerOrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Mijozlar buyurtma berishi va o'z buyurtmalarini ko'rishi uchun ViewSet.
    Faqat autentifikatsiyadan o'tgan mijozlar foydalana oladi.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.none()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Order.objects.none()
        return get_customer_orders_queryset(self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderDetailSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Mijoz o'z buyurtmasini bekor qilishi.
        """
        order = self.get_object()
        serializer = OrderCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason = serializer.validated_data.get('reason', 'Mijoz tomonidan bekor qilindi.')

        cancelled_order = order_cancel(order=order, reason=reason, user=request.user)
        return Response(OrderDetailSerializer(cancelled_order).data, status=status.HTTP_200_OK)


class CashierOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Kassirlar (va Admin) uchun buyurtmalar boshqaruvi ViewSet.
    Barcha yangi buyurtmalarni ko'rish, qabul qilish (accept), topshirish (complete)
    va bekor qilish (cancel) amallari.
    """
    permission_classes = [IsAdminOrCashier]
    filterset_class = OrderFilter
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name', 'customer__phone']
    ordering_fields = ['created_at', 'total_price', 'status']
    ordering = ['-created_at']
    serializer_class = OrderDetailSerializer
    queryset = Order.objects.none()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        return get_cashier_orders_queryset()

    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        """
        Kassir buyurtmani qabul qilishi (Status: ACCEPTED).
        Ombor qoldig'iga tegilmaydi!
        """
        order = self.get_object()
        accepted_order = order_accept(order=order, cashier_user=request.user)
        return Response(OrderDetailSerializer(accepted_order).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """
        Buyurtma mijozga topshirildi (Status: COMPLETED).
        Aynan shu bosqichda retsept bo'yicha xomashyolar ombordan chiqim qilinadi!
        """
        order = self.get_object()
        completed_order = order_complete(order=order, cashier_user=request.user)
        return Response(OrderDetailSerializer(completed_order).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        Buyurtmani bekor qilish (Status: CANCELLED).
        """
        order = self.get_object()
        serializer = OrderCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason = serializer.validated_data.get('reason', 'Kassir tomonidan bekor qilindi.')

        cancelled_order = order_cancel(order=order, reason=reason, user=request.user)
        return Response(OrderDetailSerializer(cancelled_order).data, status=status.HTTP_200_OK)
