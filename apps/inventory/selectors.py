from django.db.models import QuerySet
from apps.inventory.models import Ingredient, Supply


def get_ingredients_queryset() -> QuerySet[Ingredient]:
    """
    Xomashyolar ro'yxati selectori.
    """
    return Ingredient.objects.all().order_by('name')


def get_supplies_queryset() -> QuerySet[Supply]:
    """
    Kirimlar ro'yxati selectori (N+1 muammosini hal qilish uchun select_related ishlatiladi).
    """
    return Supply.objects.select_related('ingredient', 'created_by').order_by('-created_at')

