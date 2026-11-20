from decimal import Decimal
from rest_framework import serializers
from apps.inventory.models import Ingredient, Supply, MeasurementUnit
from apps.inventory.services import supply_create


class IngredientSerializer(serializers.ModelSerializer):
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'unit',
            'unit_display',
            'stock',
            'min_stock',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'stock', 'created_at', 'updated_at']


class SupplySerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    ingredient_unit = serializers.CharField(source='ingredient.unit', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Supply
        fields = [
            'id',
            'ingredient',
            'ingredient_name',
            'ingredient_unit',
            'quantity',
            'cost_price',
            'total_price',
            'supplier',
            'notes',
            'created_by',
            'created_by_username',
            'created_at',
        ]
        read_only_fields = ['id', 'total_price', 'created_by', 'created_at']


class SupplyCreateSerializer(serializers.Serializer):
    ingredient_id = serializers.IntegerField(required=True)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=3, required=True, min_value=Decimal('0.001'))
    cost_price = serializers.DecimalField(max_digits=14, decimal_places=2, required=True, min_value=Decimal('0'))
    supplier = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_ingredient_id(self, value):
        try:
            return Ingredient.objects.get(id=value, is_active=True)
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError("Faol bo'lgan bunday xomashyo topilmadi.")

    def create(self, validated_data):
        ingredient = validated_data.pop('ingredient_id')
        request = self.context.get('request')
        created_by = request.user if request and request.user.is_authenticated else None

        return supply_create(
            ingredient=ingredient,
            quantity=validated_data['quantity'],
            cost_price=validated_data['cost_price'],
            supplier=validated_data.get('supplier'),
            notes=validated_data.get('notes'),
            created_by=created_by,
        )

    def to_representation(self, instance):
        return SupplySerializer(instance).data

