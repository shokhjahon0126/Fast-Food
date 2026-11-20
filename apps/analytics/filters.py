import django_filters
from apps.products.models import Product


class ProductSalesRankingFilter(django_filters.FilterSet):
    """
    Mahsulotlar sotuv reytingi filtri.
    """
    category = django_filters.NumberFilter(field_name='category_id')
    is_active = django_filters.BooleanFilter(field_name='is_active')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['category', 'is_active', 'min_price', 'max_price']

