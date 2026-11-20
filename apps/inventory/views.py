from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from apps.users.permissions import IsAdminRole
from apps.inventory.selectors import get_ingredients_queryset, get_supplies_queryset
from apps.inventory.filters import IngredientFilter, SupplyFilter
from apps.inventory.serializers import (
    IngredientSerializer,
    SupplySerializer,
    SupplyCreateSerializer,
)


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Xomashyolarni boshqarish ViewSet.
    O'qish (list, retrieve): Barcha xodimlar uchun.
    Yaratish, tahrirlash, o'chirish: Faqat Administrator uchun.
    """
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    search_fields = ['name']
    ordering_fields = ['name', 'stock', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        return get_ingredients_queryset()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminRole()]


class SupplyViewSet(viewsets.ModelViewSet):
    """
    Kirim (Supply) amaliyotlarini boshqarish ViewSet.
    Faqat Administrator huquqiga ega xodimlar uchun.
    """
    permission_classes = [IsAdminRole]
    filterset_class = SupplyFilter
    search_fields = ['ingredient__name', 'supplier', 'notes']
    ordering_fields = ['created_at', 'quantity', 'total_price']
    ordering = ['-created_at']

    def get_queryset(self):
        return get_supplies_queryset()

    def get_serializer_class(self):
        if self.action == 'create':
            return SupplyCreateSerializer
        return SupplySerializer
