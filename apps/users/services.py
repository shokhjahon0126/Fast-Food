from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError, PermissionDenied
from apps.users.models import User, UserRole


def cashier_create(
    *,
    username: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
    phone: str | None = None,
) -> User:
    """
    Kassir yaratish xizmati. Faqat CASHIER roli beriladi.
    Hech kim API orqali ADMIN yarata olmaydi.
    """
    if User.objects.filter(username=username).exists():
        raise ValidationError({"username": "Bunday username allaqachon mavjud."})

    if phone and User.objects.filter(phone=phone).exists():
        raise ValidationError({"phone": "Ushbu telefon raqam allaqachon ro'yxatdan o'tgan."})

    try:
        validate_password(password)
    except DjangoValidationError as err:
        raise ValidationError({"password": list(err.messages)})

    user = User(
        username=username,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        role=UserRole.CASHIER,
        is_staff=False,
        is_superuser=False,
    )
    user.set_password(password)
    user.save()
    return user


def cashier_update(
    user: User,
    *,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
    is_active: bool | None = None,
    password: str | None = None,
) -> User:
    """
    Kassir ma'lumotlarini tahrirlash.
    Rolni o'zgartirish qat'iyan man etiladi.
    """
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    if phone is not None:
        if phone and User.objects.exclude(id=user.id).filter(phone=phone).exists():
            raise ValidationError({"phone": "Ushbu telefon raqam allaqachon ro'yxatdan o'tgan."})
        user.phone = phone
    if is_active is not None:
        user.is_active = is_active
    if password:
        try:
            validate_password(password, user=user)
        except DjangoValidationError as err:
            raise ValidationError({"password": list(err.messages)})
        user.set_password(password)

    user.save()
    return user


def cashier_delete(current_user: User, target_user: User) -> None:
    """
    Foydalanuvchini o'chirish qoidalari:
    1. Admin o'zini o'zi o'chira olmaydi.
    2. Admin boshqa Adminni o'chira olmaydi.
    3. Faqat Kassir rolidagi foydalanuvchini o'chirish mumkin.
    """
    if current_user.id == target_user.id:
        raise ValidationError(
            {"detail": "Administrator o'zining shaxsiy hisobini o'chira olmaydi."}
        )

    if target_user.role == UserRole.ADMIN or target_user.is_superuser:
        raise PermissionDenied(
            "Administrator boshqa Administrator hisobini o'chirish huquqiga ega emas."
        )

    if target_user.role != UserRole.CASHIER:
        raise PermissionDenied(
            "Faqat Kassir rolidagi xodimlarni o'chirish mumkin."
        )

    target_user.delete()

