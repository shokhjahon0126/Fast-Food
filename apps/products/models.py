from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """
    Menyu toifalari (Burgerlar, Lavashlar, Ichimliklar, Souslar va h.k.)
    """
    name = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        verbose_name=_('Kategoriya nomi')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Tartib raqami')
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Faol')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Kategoriya')
        verbose_name_plural = _('Kategoriyalar')
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['order', 'is_active']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Tayyor menyu mahsuloti / taom (Chizburger, Lavash, Hot-dog va h.k.)
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('Kategoriya')
    )
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name=_('Mahsulot nomi')
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Sotuv narxi (so‘m)')
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name=_('Tavsifi')
    )
    image = models.FileField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name=_('Rasmi')
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Sotuvda mavjud')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Mahsulot')
        verbose_name_plural = _('Mahsulotlar')
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return f"{self.name} - {self.price:,.0f} so'm"


class ProductRecipe(models.Model):
    """
    Mahsulot retsepti (BOM - Bill of Materials).
    Bitta tayyor taom (masalan: 1 ta Burger) uchun qaysi xomashyodan (Ingredient)
    qancha miqdorda sarflanishini belgilaydi.
    Misol: 1 ta Burger uchun:
      - Burger noni: 1 dona
      - Kotlet: 2 dona
      - Pomidor: 0.050 kg (yoki 1 dona)
      - Sous: 20 gr
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('Tayyor mahsulot')
    )
    ingredient = models.ForeignKey(
        'inventory.Ingredient',
        on_delete=models.PROTECT,
        related_name='used_in_recipes',
        verbose_name=_('Kerakli xomashyo')
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name=_('Sarflanadigan miqdor')
    )

    class Meta:
        verbose_name = _('Retsept tarkibi')
        verbose_name_plural = _('Retsept tarkiblari')
        unique_together = ['product', 'ingredient']
        indexes = [
            models.Index(fields=['product', 'ingredient']),
        ]

    def __str__(self):
        return f"{self.product.name} <- {self.quantity} {self.ingredient.unit} {self.ingredient.name}"
