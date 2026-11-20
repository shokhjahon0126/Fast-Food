import django_filters
from apps.products.models import Category, Product


class CategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Category
        fields = ['name', 'is_active']


class ProductFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='category_id')
    name = django_filters.CharFilter(lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Product
        fields = ['category', 'name', 'min_price', 'max_price', 'is_active']

