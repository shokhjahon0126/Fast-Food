from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import (
    Sum,
    Count,
    F,
    Q,
    IntegerField,
    DecimalField,
    QuerySet,
)
from django.db.models.functions import Coalesce, TruncDate
from apps.orders.models import Order, OrderStatus
from apps.products.models import Product


def get_sales_overview() -> dict:
    """
    Administrator Dashboard uchun umumiy sotuvlar va tushum tahlili.
    Bitta yuqori optimizatsiyalashgan SQL so'rov orqali quyidagilarni hisoblaydi:
    - Bugungi tushum va buyurtmalar soni (Daily)
    - Oxirgi 7 kunlik tushum va buyurtmalar soni (Weekly)
    - Oxirgi 30 kunlik tushum va buyurtmalar soni (Monthly)
    - Jami barcha vaqtlardagi tushum va topshirilgan buyurtmalar soni
    - Buyurtmalar statuslari kesimi (COMPLETED, CANCELLED, PENDING, ACCEPTED)
    - Bekor qilingan buyurtmalar sababli yo'qotilgan summa
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    stats = Order.objects.aggregate(
        # Bugungi kun
        today_revenue=Coalesce(
            Sum('total_price', filter=Q(status=OrderStatus.COMPLETED, created_at__gte=today_start)),
            Decimal('0.00'),
            output_field=DecimalField(max_digits=14, decimal_places=2)
        ),
        today_orders=Count(
            'id',
            filter=Q(status=OrderStatus.COMPLETED, created_at__gte=today_start)
        ),

        # Haftalik (oxirgi 7 kun)
        weekly_revenue=Coalesce(
            Sum('total_price', filter=Q(status=OrderStatus.COMPLETED, created_at__gte=seven_days_ago)),
            Decimal('0.00'),
            output_field=DecimalField(max_digits=14, decimal_places=2)
        ),
        weekly_orders=Count(
            'id',
            filter=Q(status=OrderStatus.COMPLETED, created_at__gte=seven_days_ago)
        ),

        # Oylik (oxirgi 30 kun)
        monthly_revenue=Coalesce(
            Sum('total_price', filter=Q(status=OrderStatus.COMPLETED, created_at__gte=thirty_days_ago)),
            Decimal('0.00'),
            output_field=DecimalField(max_digits=14, decimal_places=2)
        ),
        monthly_orders=Count(
            'id',
            filter=Q(status=OrderStatus.COMPLETED, created_at__gte=thirty_days_ago)
        ),

        # Jami barcha vaqtlardagi
        total_revenue=Coalesce(
            Sum('total_price', filter=Q(status=OrderStatus.COMPLETED)),
            Decimal('0.00'),
            output_field=DecimalField(max_digits=14, decimal_places=2)
        ),

        # Statuslar bo'yicha buyurtmalar soni
        completed_orders=Count('id', filter=Q(status=OrderStatus.COMPLETED)),
        cancelled_orders=Count('id', filter=Q(status=OrderStatus.CANCELLED)),
        pending_orders=Count('id', filter=Q(status=OrderStatus.PENDING)),
        accepted_orders=Count('id', filter=Q(status=OrderStatus.ACCEPTED)),
        total_orders=Count('id'),

        # Bekor bo'lgan buyurtmalar summasi (yo'qotilgan summa)
        cancelled_revenue_loss=Coalesce(
            Sum('total_price', filter=Q(status=OrderStatus.CANCELLED)),
            Decimal('0.00'),
            output_field=DecimalField(max_digits=14, decimal_places=2)
        ),
    )

    return stats


def get_products_sales_ranking_queryset(
    start_date=None,
    end_date=None,
    category_id=None,
) -> QuerySet[Product]:
    """
    Mahsulotlarning sotuv reytingi queryseti.
    Har bir mahsulot bo'yicha jami sotilgan miqdor (total_sold_quantity)
    va jami keltirilgan daromad (total_revenue) ni hisoblaydi.
    N+1 muammosini oldini olish uchun kategoriya select_related orqali olinadi.
    """
    order_filter = Q(order_items__order__status=OrderStatus.COMPLETED)

    if start_date:
        order_filter &= Q(order_items__order__created_at__date__gte=start_date)
    if end_date:
        order_filter &= Q(order_items__order__created_at__date__lte=end_date)

    qs = Product.objects.select_related('category').annotate(
        total_sold_quantity=Coalesce(
            Sum('order_items__quantity', filter=order_filter),
            0,
            output_field=IntegerField()
        ),
        total_revenue=Coalesce(
            Sum(
                F('order_items__quantity') * F('order_items__unit_price'),
                filter=order_filter
            ),
            Decimal('0.00'),
            output_field=DecimalField(max_digits=14, decimal_places=2)
        ),
    )

    if category_id:
        qs = qs.filter(category_id=category_id)

    return qs


def get_top_selling_products(limit: int = 5) -> list[Product]:
    """
    Eng ko'p sotilgan top N ta mahsulot.
    """
    return list(
        get_products_sales_ranking_queryset()
        .order_by('-total_sold_quantity', '-total_revenue')[:limit]
    )


def get_least_selling_products(limit: int = 5) -> list[Product]:
    """
    Eng kam sotilgan (yoki sotilishi to'xtagan) N ta mahsulot.
    """
    return list(
        get_products_sales_ranking_queryset()
        .order_by('total_sold_quantity', 'total_revenue')[:limit]
    )


def get_sales_trend(days: int = 30, start_date=None, end_date=None) -> list[dict]:
    """
    Kunlar kesimidagi sotuvlar grafigi (trend).
    Har bir sana bo'yicha yakunlangan buyurtmalar soni va kunlik daromadni qaytaradi.
    """
    qs = Order.objects.filter(status=OrderStatus.COMPLETED)

    if start_date and end_date:
        qs = qs.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    else:
        since_date = timezone.now() - timedelta(days=days)
        qs = qs.filter(created_at__gte=since_date)

    trend_data = (
        qs.annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(
            orders_count=Count('id'),
            total_revenue=Coalesce(
                Sum('total_price'),
                Decimal('0.00'),
                output_field=DecimalField(max_digits=14, decimal_places=2)
            ),
        )
        .order_by('date')
    )

    return list(trend_data)
