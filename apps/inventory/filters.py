import django_filters
from django.db.models import F
from apps.inventory.models import Ingredient, Supply


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    unit = django_filters.CharFilter(lookup_expr='exact')
    is_active = django_filters.BooleanFilter()
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')

    class Meta:
        model = Ingredient
        fields = ['name', 'unit', 'is_active', 'low_stock']

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lte=F('min_stock'))
        return queryset


class SupplyFilter(django_filters.FilterSet):
    ingredient = django_filters.NumberFilter(field_name='ingredient_id')
    supplier = django_filters.CharFilter(lookup_expr='icontains')
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Supply
        fields = ['ingredient', 'supplier', 'date_from', 'date_to']

