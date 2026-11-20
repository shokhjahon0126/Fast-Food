from decimal import Decimal
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.inventory.models import Ingredient, Supply


@transaction.atomic
def supply_create(
    *,
    ingredient: Ingredient,
    quantity: Decimal,
    cost_price: Decimal,
    supplier: str | None = None,
    notes: str | None = None,
    created_by=None,
) -> Supply:
    """
    Omborga xomashyo kirim qilish biznes mantiqi.
    Tranzaksiya ichida Supply yozuvi yaratiladi va
    tegishli Ingredient ning ombordagi qoldig'i (stock) avtomatik oshiriladi.
    """
    if quantity <= Decimal('0'):
        raise ValidationError({"quantity": "Kirim miqdori 0 dan katta bo'lishi shart."})

    if cost_price < Decimal('0'):
        raise ValidationError({"cost_price": "Kirim narxi manfiy bo'lishi mumkin emas."})

    supply = Supply.objects.create(
        ingredient=ingredient,
        quantity=quantity,
        cost_price=cost_price,
        supplier=supplier,
        notes=notes,
        created_by=created_by,
    )

    ingredient.refresh_from_db()
    return supply
