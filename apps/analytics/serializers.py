from rest_framework import serializers
from apps.products.models import Product


class ProductSalesRankingSerializer(serializers.ModelSerializer):
    """
    Mahsulotning sotuv reytingi va daromad ko'rsatkichi.
    """
    category_id = serializers.IntegerField(source='category.id', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_sold_quantity = serializers.IntegerField(read_only=True)
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'category_id',
            'category_name',
            'price',
            'is_active',
            'total_sold_quantity',
            'total_revenue',
        ]


class SalesMetricItemSerializer(serializers.Serializer):
    """
    Muayyan davr (kunlik, haftalik, oylik) bo'yicha daromad va buyurtmalar soni.
    """
    revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    orders_count = serializers.IntegerField()


class OrderStatusBreakdownSerializer(serializers.Serializer):
    """
    Buyurtmalar statuslari kesimidagi taqsimot.
    """
    completed = serializers.IntegerField()
    cancelled = serializers.IntegerField()
    pending = serializers.IntegerField()
    accepted = serializers.IntegerField()
    total = serializers.IntegerField()
    cancelled_revenue_loss = serializers.DecimalField(max_digits=14, decimal_places=2)


class DashboardOverviewSerializer(serializers.Serializer):
    """
    Admin Dashboard asosiy konsolidatsiyalangan statistikasi.
    """
    daily = SalesMetricItemSerializer()
    weekly = SalesMetricItemSerializer()
    monthly = SalesMetricItemSerializer()
    all_time_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    order_statuses = OrderStatusBreakdownSerializer()
    top_selling_products = ProductSalesRankingSerializer(many=True)
    least_selling_products = ProductSalesRankingSerializer(many=True)


class SalesTrendItemSerializer(serializers.Serializer):
    """
    Kunlik sotuv trendining bitta nuqtasi.
    """
    date = serializers.DateField()
    orders_count = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)


class SalesTrendQuerySerializer(serializers.Serializer):
    """
    Trend grafigi so'rovi uchun filtr parametrlari.
    """
    days = serializers.IntegerField(required=False, default=30, min_value=1, max_value=365)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({"start_date": "start_date end_date dan katta bo'lishi mumkin emas."})
        return attrs
