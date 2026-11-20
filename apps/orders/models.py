from decimal import Decimal
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class OrderStatus(models.TextChoices):
    PENDING = 'pending', _('Kutilmoqda (Yangi)')
    ACCEPTED = 'accepted', _('Qabul qilindi (Tayyorlanmoqda)')
    COMPLETED = 'completed', _('Topshirildi (Yakunlandi)')
    CANCELLED = 'cancelled', _('Bekor qilindi')


class OrderType(models.TextChoices):
    DINE_IN = 'dine_in', _('Joyida')
    TAKEAWAY = 'takeaway', _('Olib ketish')
    DELIVERY = 'delivery', _('Yetkazib berish')


class PaymentType(models.TextChoices):
    CASH = 'cash', _('Naqd pul')
    CARD = 'card', _('Plastik karta')
    ONLINE = 'online', _('Click / Payme')


def generate_order_number() -> str:
    return f"FF-{uuid.uuid4().hex[:8].upper()}"


class Order(models.Model):
    """
    Buyurtma modeli.
    Mijoz tomonidan yaratiladi (PENDING).
    Kassir qabul qiladi (ACCEPTED - bu bosqichda omborga tegilmaydi).
    Buyurtma topshirilganda (COMPLETED) ombordan xomashyo retsept bo'yicha chiqim qilinadi.
    """
    order_number = models.CharField(
        max_length=32,
        unique=True,
        default=generate_order_number,
        db_index=True,
        verbose_name=_('Buyurtma raqami')
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('Mijoz')
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True,
        verbose_name=_('Holati')
    )
    order_type = models.CharField(
        max_length=20,
        choices=OrderType.choices,
        default=OrderType.TAKEAWAY,
        verbose_name=_('Buyurtma turi')
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        default=PaymentType.CASH,
        verbose_name=_('To‘lov usuli')
    )
    delivery_address = models.TextField(
        blank=True,
        default='',
        verbose_name=_('Yetkazib berish manzili')
    )
    total_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Umumiy summa (so‘m)')
    )
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_orders',
        verbose_name=_('Qabul qilgan kassir')
    )
    is_stock_deducted = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Ombordagi xomashyo chiqim qilinganmi')
    )
    cancellation_reason = models.TextField(
        blank=True,
        default='',
        verbose_name=_('Bekor qilish sababi')
    )
    notes = models.TextField(
        blank=True,
        default='',
        verbose_name=_('Izoh')
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Buyurtma')
        verbose_name_plural = _('Buyurtmalar')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['order_number']),
        ]

    def __str__(self):
        return f"{self.order_number} - {self.customer.get_full_name() or self.customer.username} ({self.get_status_display()})"


class OrderItem(models.Model):
    """
    Buyurtmadagi alohida taom/mahsulot va uning miqdori.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Buyurtma')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name=_('Mahsulot')
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Miqdori')
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Birlik narxi (so‘m)')
    )
    total_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name=_('Jami narxi (so‘m)')
    )
    notes = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_('Taomga izoh (masalan: piyozsiz)')
    )

    class Meta:
        verbose_name = _('Buyurtma tarkibi')
        verbose_name_plural = _('Buyurtma tarkiblari')

    def save(self, *args, **kwargs):
        if self.quantity and self.unit_price:
            self.total_price = Decimal(self.quantity) * Decimal(self.unit_price)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order.order_number}: {self.product.name} x {self.quantity}"
