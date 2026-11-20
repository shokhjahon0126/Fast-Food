from django.db.models import QuerySet
from apps.products.models import Category, Product, ProductRecipe


def get_categories_queryset() -> QuerySet[Category]:
    """
    Kategoriyalar ro'yxati selectori.
    """
    return Category.objects.all().order_by('order', 'name')


def get_products_queryset() -> QuerySet[Product]:
    """
    Mahsulotlar ro'yxati selectori.
    N+1 muammosini yo'qotish uchun category ga select_related,
    retsept xomashyolariga esa prefetch_related qilinadi.
    """
    return (
        Product.objects.select_related('category')
        .prefetch_related('recipes__ingredient')
        .order_by('category__order', 'name')
    )


def get_recipes_queryset() -> QuerySet[ProductRecipe]:
    """
    Retseptlar selectori (product va ingredient ga select_related bilan).
    """
    return ProductRecipe.objects.select_related('product', 'ingredient').order_by('product__name')

