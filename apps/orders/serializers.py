from rest_framework import serializers
from apps.orders.models import Order, OrderItem, OrderStatus, OrderType, PaymentType
from apps.orders.services import order_create, telegram_order_create


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True, required=True)
    order_type = serializers.ChoiceField(choices=OrderType.choices, default=OrderType.TAKEAWAY)
    payment_type = serializers.ChoiceField(choices=PaymentType.choices, default=PaymentType.CASH)
    delivery_address = serializers.CharField(required=False, allow_blank=True, default='')
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Kamida bitta mahsulot kiritilishi shart.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        customer = request.user
        items_data = validated_data.pop('items')

        return order_create(
            customer=customer,
            items_data=items_data,
            **validated_data
        )

    def to_representation(self, instance):
        return OrderDetailSerializer(instance).data


class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'category_name',
            'quantity',
            'unit_price',
            'total_price',
            'notes',
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemDetailSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    accepted_by_username = serializers.CharField(source='accepted_by.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'customer',
            'customer_name',
            'customer_phone',
            'status',
            'status_display',
            'order_type',
            'payment_type',
            'delivery_address',
            'total_price',
            'accepted_by',
            'accepted_by_username',
            'is_stock_deducted',
            'cancellation_reason',
            'notes',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class OrderCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default='Mijoz yoki kassir tomonidan bekor qilindi.')


class TelegramOrderCreateSerializer(serializers.Serializer):
    """
    Telegram WebApp orqali buyurtma berish uchun serializer.
    Telegram foydalanuvchisi va buyurtma ma'lumotlarini qabul qiladi.
    """
    telegram_id = serializers.IntegerField(required=True)
    phone = serializers.CharField(required=True, max_length=30)
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')
    telegram_username = serializers.CharField(required=False, allow_blank=True, default='')
    items = OrderItemInputSerializer(many=True, required=True)
    order_type = serializers.ChoiceField(choices=OrderType.choices, default=OrderType.TAKEAWAY)
    payment_type = serializers.ChoiceField(choices=PaymentType.choices, default=PaymentType.CASH)
    delivery_address = serializers.CharField(required=False, allow_blank=True, default='')
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Kamida bitta mahsulot kiritilishi shart.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        return telegram_order_create(
            items_data=items_data,
            **validated_data
        )

    def to_representation(self, instance):
        return OrderDetailSerializer(instance).data

