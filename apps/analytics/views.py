from rest_framework import views, generics, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from apps.users.permissions import IsAdminRole
from apps.products.models import Product
from apps.analytics.selectors import (
    get_sales_overview,
    get_products_sales_ranking_queryset,
    get_top_selling_products,
    get_least_selling_products,
    get_sales_trend,
)
from apps.analytics.filters import ProductSalesRankingFilter
from apps.analytics.serializers import (
    DashboardOverviewSerializer,
    ProductSalesRankingSerializer,
    SalesTrendItemSerializer,
    SalesTrendQuerySerializer,
)


class DashboardOverviewView(views.APIView):
    """
    Administrator Dashboard asosiy ma'lumotlari.
    Kunlik, haftalik, oylik tushum, buyurtmalar statusi va
    eng ko'p / eng kam sotilgan mahsulotlar jamlanmasini qaytaradi.
    """
    permission_classes = [IsAdminRole]

    @extend_schema(
        tags=['Analytics & Dashboard'],
        summary="Admin Dashboard umumiy ko'rsatkichlari",
        description="Kunlik, haftalik, oylik tushum, buyurtmalar statusi taqsimoti va top/past mahsulotlar reytingi.",
        responses={200: DashboardOverviewSerializer},
    )
    def get(self, request, *args, **kwargs):
        overview_stats = get_sales_overview()
        top_products = get_top_selling_products(limit=5)
        least_products = get_least_selling_products(limit=5)

        data = {
            'daily': {
                'revenue': overview_stats['today_revenue'],
                'orders_count': overview_stats['today_orders'],
            },
            'weekly': {
                'revenue': overview_stats['weekly_revenue'],
                'orders_count': overview_stats['weekly_orders'],
            },
            'monthly': {
                'revenue': overview_stats['monthly_revenue'],
                'orders_count': overview_stats['monthly_orders'],
            },
            'all_time_revenue': overview_stats['total_revenue'],
            'order_statuses': {
                'completed': overview_stats['completed_orders'],
                'cancelled': overview_stats['cancelled_orders'],
                'pending': overview_stats['pending_orders'],
                'accepted': overview_stats['accepted_orders'],
                'total': overview_stats['total_orders'],
                'cancelled_revenue_loss': overview_stats['cancelled_revenue_loss'],
            },
            'top_selling_products': ProductSalesRankingSerializer(top_products, many=True).data,
            'least_selling_products': ProductSalesRankingSerializer(least_products, many=True).data,
        }

        serializer = DashboardOverviewSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductSalesRankingView(generics.ListAPIView):
    """
    Barcha mahsulotlarning to'liq sotuv reytingi.
    Jami sotilgan miqdor (total_sold_quantity) yoki jami tushum (total_revenue)
    bo'yicha o'sish/kamayish tartibida saralash, sana oralig'i va kategoriya filtri mavjud.
    """
    permission_classes = [IsAdminRole]
    serializer_class = ProductSalesRankingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductSalesRankingFilter
    search_fields = ['name']
    ordering_fields = ['total_sold_quantity', 'total_revenue', 'price', 'name']
    ordering = ['-total_sold_quantity', '-total_revenue']
    queryset = Product.objects.none()

    @extend_schema(
        tags=['Analytics & Dashboard'],
        summary="Mahsulotlar sotuv reytingi",
        description="Mahsulotlar bo'yicha sotuv miqdori va keltirilgan tushum reytingi (saralash va filtrlar bilan).",
        parameters=[
            OpenApiParameter(name='start_date', description="Boshlang'ich sana (YYYY-MM-DD)", required=False, type=str),
            OpenApiParameter(name='end_date', description="Tugash sanasi (YYYY-MM-DD)", required=False, type=str),
        ],
        responses={200: ProductSalesRankingSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Product.objects.none()

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        return get_products_sales_ranking_queryset(
            start_date=start_date,
            end_date=end_date,
        )


class SalesTrendView(views.APIView):
    """
    Kunlar kesimidagi dinamik sotuvlar grafigi (trend).
    """
    permission_classes = [IsAdminRole]

    @extend_schema(
        tags=['Analytics & Dashboard'],
        summary="Kunlik sotuvlar trendi (grafik uchun)",
        description="Kunlar kesimida buyurtmalar soni va kunlik tushum dinamikasi.",
        parameters=[
            OpenApiParameter(name='days', description="Oxirgi necha kunlik trend (default: 30)", required=False, type=int),
            OpenApiParameter(name='start_date', description="Boshlang'ich sana (YYYY-MM-DD)", required=False, type=str),
            OpenApiParameter(name='end_date', description="Tugash sanasi (YYYY-MM-DD)", required=False, type=str),
        ],
        responses={200: SalesTrendItemSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        query_serializer = SalesTrendQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        validated = query_serializer.validated_data

        days = validated.get('days', 30)
        start_date = validated.get('start_date')
        end_date = validated.get('end_date')

        trend_data = get_sales_trend(
            days=days,
            start_date=start_date,
            end_date=end_date,
        )

        serializer = SalesTrendItemSerializer(trend_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

