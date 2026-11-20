from decimal import Decimal
from django.db import models
from django.db.models import F
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class MeasurementUnit(models.TextChoices):
    KG = 'kg', _('Kilogramm (kg)')
    G = 'g', _('Gramm (g)')
    L = 'l', _('Litr (l)')
    ML = 'ml', _('Millilitr (ml)')
    PIECE = 'piece', _('Dona (dona)')


class Ingredient(models.Model):
    """
    Ombordagi barcha xomashyolar (unikal baza):
    Misol uchun: Tovuq go'shti (file), Burger noni, Pomidor, Pishloq va h.k.
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name=_('Xomashyo nomi')
    )
    unit = models.CharField(
        max_length=20,
        choices=MeasurementUnit.choices,
        default=MeasurementUnit.KG,
        verbose_name=_("O'lchov birligi")
    )
    stock = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000'),
        verbose_name=_('Ombordagi qoldiq')
    )
    min_stock = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000'),
        verbose_name=_('Minimal ogohlantirish qoldig‘i')
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Faol')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Xomashyo')
        verbose_name_plural = _('Xomashyolar')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['unit']),
        ]

    def __str__(self):
        return f"{self.name} ({self.stock} {self.get_unit_display()})"


class Supply(models.Model):
    """
    Omborga xomashyo kirim qilish amaliyoti (Kirim/Inflow).
    Har bir kirim qilinganda xomashyoning joriy qoldig'i avtomatik oshiriladi.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='supplies',
        verbose_name=_('Xomashyo')
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        verbose_name=_('Kirim miqdori')
    )
    cost_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name=_('Birlik narxi (so‘m)')
    )
    total_price = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('Umumiy summa (so‘m)')
    )
    supplier = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Ta’minotchi')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Izoh')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_supplies',
        verbose_name=_('Qabul qilgan xodim')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_('Kirim sanasi')
    )

    class Meta:
        verbose_name = _('Kirim')
        verbose_name_plural = _('Kirimlar')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['ingredient', 'created_at']),
        ]

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if self.quantity and self.cost_price:
            self.total_price = Decimal(self.quantity) * Decimal(self.cost_price)
        super().save(*args, **kwargs)
        if is_new and self.ingredient_id and self.quantity:
            Ingredient.objects.filter(id=self.ingredient_id).update(
                stock=F('stock') + Decimal(self.quantity)
            )

    def delete(self, *args, **kwargs):
        ingredient_id = self.ingredient_id
        quantity = self.quantity
        result = super().delete(*args, **kwargs)
        if ingredient_id and quantity:
            Ingredient.objects.filter(id=ingredient_id).update(
                stock=F('stock') - Decimal(quantity)
            )
        return result

    def __str__(self):
        return f"{self.ingredient.name} +{self.quantity} {self.ingredient.unit} ({self.created_at:%Y-%m-%d %H:%M})"
