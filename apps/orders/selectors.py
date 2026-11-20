from django.db.models import QuerySet, Prefetch
from apps.orders.models import Order, OrderItem


def get_orders_base_queryset() -> QuerySet[Order]:
    """
    Buyurtmalar uchun N+1 muammosidan xoli yuqori unumdorlikdagi selector.
    Mijoz, qabul qilgan kassir, va buyurtma ichidagi mahsulotlar hamda
    ularning kategoriyalarini optimal select_related orqali 3 ta so'rovda yuklaydi.
    """
    items_prefetch = Prefetch(
        'items',
        queryset=OrderItem.objects.select_related('product__category')
    )

    return (
        Order.objects.select_related('customer', 'accepted_by')
        .prefetch_related(items_prefetch)
        .order_by('-created_at')
    )


def get_customer_orders_queryset(customer) -> QuerySet[Order]:
    """
    Mijozning o'ziga tegishli buyurtmalar ro'yxati.
    """
    if not customer or not getattr(customer, "is_authenticated", False):
        return Order.objects.none()
    return get_orders_base_queryset().filter(customer=customer)


def get_cashier_orders_queryset() -> QuerySet[Order]:
    """
    Kassir ko'rishi mumkin bo'lgan barcha buyurtmalar ro'yxati.
    """
    return get_orders_base_queryset()
