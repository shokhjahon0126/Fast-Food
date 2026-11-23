from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class UserRole(models.TextChoices):
    ADMIN = 'admin', _('Admin')
    CASHIER = 'cashier', _('Cashier')
    CUSTOMER = 'customer', _('Mijoz')


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CASHIER,
        db_index=True,
        verbose_name=_('Role'),
    )
    phone = PhoneNumberField(
        region="UZ",
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('Phone Number'),
    )
    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('Telegram ID'),
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-id']
        indexes = [
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['username']),
            models.Index(fields=['telegram_id']),
        ]

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_cashier(self) -> bool:
        return self.role == UserRole.CASHIER

    @property
    def is_customer(self) -> bool:
        return self.role == UserRole.CUSTOMER

    def __str__(self):
        full_name = self.get_full_name()
        if full_name:
            return f"{full_name} ({self.username}) - {self.get_role_display()}"
        return f"{self.username} - {self.get_role_display()}"
