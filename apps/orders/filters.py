import django_filters
from apps.orders.models import Order, OrderStatus, OrderType


class OrderFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=OrderStatus.choices)
    order_type = django_filters.ChoiceFilter(choices=OrderType.choices)
    customer = django_filters.NumberFilter(field_name='customer_id')
    order_number = django_filters.CharFilter(lookup_expr='icontains')
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Order
        fields = ['status', 'order_type', 'customer', 'order_number', 'date_from', 'date_to']

