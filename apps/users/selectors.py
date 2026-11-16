from django.db.models import QuerySet
from apps.users.models import User, UserRole


def get_cashiers_queryset() -> QuerySet[User]:
    """
    Kassirlar ro'yxatini qaytaruvchi optimallashtirilgan selector.
    """
    return (
        User.objects.filter(role=UserRole.CASHIER)
        .only(
            'id',
            'username',
            'first_name',
            'last_name',
            'phone',
            'role',
            'is_active',
            'date_joined',
        )
        .order_by('-id')
    )


def get_user_by_id(user_id: int) -> User | None:
    """
    ID bo'yicha foydalanuvchini olish.
    """
    return User.objects.filter(id=user_id).first()

