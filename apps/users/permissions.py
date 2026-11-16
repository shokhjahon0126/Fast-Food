from rest_framework.permissions import BasePermission
from apps.users.models import UserRole


class IsAdminRole(BasePermission):
    """
    Ruxsat faqat Admin rolidagi yoki superuser bo'lgan foydalanuvchilarga beriladi.
    """
    message = "Ushbu amalni faqat Administrator bajarishi mumkin."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == UserRole.ADMIN or request.user.is_superuser)
        )


class IsCashierRole(BasePermission):
    """
    Ruxsat faqat Kassir rolidagi foydalanuvchilarga beriladi.
    """
    message = "Ushbu amalni faqat Kassir bajarishi mumkin."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.CASHIER
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Obyekt egasi yoki Admin uchun ruxsat.
    """
    message = "Siz faqat o'zingizning ma'lumotlaringizni ko'ra olasiz yoki tahrirlay olasiz."

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role == UserRole.ADMIN or request.user.is_superuser:
            return True
        return obj == request.user

