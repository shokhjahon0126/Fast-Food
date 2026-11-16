import django_filters
from apps.users.models import User


class CashierFilter(django_filters.FilterSet):
    phone = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    date_joined_after = django_filters.DateTimeFilter(field_name='date_joined', lookup_expr='gte')
    date_joined_before = django_filters.DateTimeFilter(field_name='date_joined', lookup_expr='lte')

    class Meta:
        model = User
        fields = ['phone', 'is_active', 'date_joined_after', 'date_joined_before']

