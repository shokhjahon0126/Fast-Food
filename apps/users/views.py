from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.users.permissions import IsAdminRole
from apps.users.selectors import get_cashiers_queryset
from apps.users.services import cashier_delete
from apps.users.filters import CashierFilter
from apps.users.serializers import (
    CashierSerializer,
    CashierCreateSerializer,
    CashierUpdateSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    CustomerRegisterSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Foydalanuvchi login qilganda access, refresh, id va role qaytaruvchi view.
    """
    serializer_class = CustomTokenObtainPairSerializer


class CashierViewSet(viewsets.ModelViewSet):
    """
    Kassirlarni boshqarish uchun ViewSet.
    Faqat Administrator ruxsatiga ega bo'lgan foydalanuvchilar kira oladi.
    """
    permission_classes = [IsAdminRole]
    filterset_class = CashierFilter
    search_fields = ['username', 'first_name', 'last_name', 'phone']
    ordering_fields = ['id', 'username', 'date_joined']
    ordering = ['-id']

    def get_queryset(self):
        return get_cashiers_queryset()

    def get_serializer_class(self):
        if self.action == 'create':
            return CashierCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CashierUpdateSerializer
        return CashierSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        cashier_delete(current_user=request.user, target_user=instance)
        return Response(
            {"detail": "Kassir muvaffaqiyatli o'chirildi."},
            status=status.HTTP_204_NO_CONTENT,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Foydalanuvchining shaxsiy profiling ko'rish va tahrirlash (/api/v1/users/me/).
    Admin va Kassir o'z shaxsiy ma'lumotlarini o'zgartirishi mumkin,
    lekin rolni o'zgartira olmaydi.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class CustomerRegisterView(generics.CreateAPIView):
    """
    Ommaviy ro'yxatdan o'tish (Public Registration).
    Istalgan yangi mijoz ro'yxatdan o'ta oladi. Rol avtomatik CUSTOMER bo'ladi.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomerRegisterSerializer
