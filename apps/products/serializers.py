from decimal import Decimal
from rest_framework import serializers
from apps.products.models import Category, Product, ProductRecipe
from apps.products.services import set_product_recipe


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(source='products.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'order', 'is_active', 'products_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductRecipeSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    ingredient_unit = serializers.CharField(source='ingredient.unit', read_only=True)
    ingredient_unit_display = serializers.CharField(source='ingredient.get_unit_display', read_only=True)
    current_stock = serializers.DecimalField(source='ingredient.stock', max_digits=12, decimal_places=3, read_only=True)

    class Meta:
        model = ProductRecipe
        fields = [
            'id',
            'product',
            'ingredient',
            'ingredient_name',
            'ingredient_unit',
            'ingredient_unit_display',
            'current_stock',
            'quantity',
        ]
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    recipes = ProductRecipeSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'category_name',
            'name',
            'price',
            'description',
            'image',
            'is_active',
            'recipes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RecipeItemInputSerializer(serializers.Serializer):
    ingredient_id = serializers.IntegerField(required=True)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=3, required=True, min_value=Decimal('0.001'))


class SetProductRecipeSerializer(serializers.Serializer):
    items = RecipeItemInputSerializer(many=True, required=True)

    def save(self, product):
        return set_product_recipe(product, self.validated_data['items'])

