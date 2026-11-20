from decimal import Decimal
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.inventory.models import Ingredient
from apps.products.models import Product, ProductRecipe


@transaction.atomic
def set_product_recipe(product: Product, recipe_items: list[dict]) -> list[ProductRecipe]:
    """
    Mahsulotning to'liq retseptini yangilash yoki o'rnatish xizmati.
    Tranzaksiya ichida eski retseptlar o'rniga yangilari o'rnatiladi.
    Misol recipe_items:
      [
        {"ingredient_id": 1, "quantity": Decimal("1.000")}, # 1 dona non
        {"ingredient_id": 2, "quantity": Decimal("2.000")}, # 2 dona kotlet
      ]
    """
    ingredient_ids = [item['ingredient_id'] for item in recipe_items]
    existing_ingredients = {ing.id: ing for ing in Ingredient.objects.filter(id__in=ingredient_ids)}

    for item in recipe_items:
        ing_id = item['ingredient_id']
        qty = item['quantity']

        if ing_id not in existing_ingredients:
            raise ValidationError({"ingredient_id": f"ID={ing_id} bo'lgan xomashyo topilmadi."})

        if Decimal(qty) <= Decimal('0'):
            raise ValidationError({"quantity": "Retsept miqdori 0 dan katta bo'lishi shart."})

    # Eski retseptlarni tozalash
    product.recipes.all().delete()

    # Yangi retseptlarni yaratish
    created_recipes = [
        ProductRecipe(
            product=product,
            ingredient_id=item['ingredient_id'],
            quantity=item['quantity'],
        )
        for item in recipe_items
    ]
    ProductRecipe.objects.bulk_create(created_recipes)

    return list(product.recipes.select_related('ingredient').all())

