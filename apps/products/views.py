from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.users.permissions import IsAdminRole
from apps.products.selectors import (
    get_categories_queryset,
    get_products_queryset,
    get_recipes_queryset,
)
from apps.products.filters import CategoryFilter, ProductFilter
from apps.products.serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductRecipeSerializer,
    SetProductRecipeSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Kategoriyalarni boshqarish ViewSet.
    O'qish: Barcha xodimlar uchun.
    O'zgartirish/Yaratish: Faqat Administrator.
    """
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter
    search_fields = ['name']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']

    def get_queryset(self):
        return get_categories_queryset()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminRole()]


class ProductViewSet(viewsets.ModelViewSet):
    """
    Mahsulotlar (Menyu) ViewSet.
    O'qish: Barcha xodimlar uchun (Kassir ham menyuni ko'ra oladi).
    O'zgartirish/Yaratish: Faqat Administrator.
    """
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'name', 'created_at', 'category__order']
    ordering = ['category__order', 'name']

    def get_queryset(self):
        return get_products_queryset()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminRole()]

    @action(detail=True, methods=['post'], url_path='set-recipe', permission_classes=[IsAdminRole])
    def set_recipe(self, request, pk=None):
        """
        Mahsulot uchun retseptni (tarkibni) to'liq sozlash yoki yangilash.
        Misol:
        {
          "items": [
            {"ingredient_id": 1, "quantity": "1.000"},
            {"ingredient_id": 2, "quantity": "2.000"}
          ]
        }
        """
        product = self.get_object()
        serializer = SetProductRecipeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipes = serializer.save(product=product)

        return Response(
            ProductRecipeSerializer(recipes, many=True).data,
            status=status.HTTP_200_OK
        )


class ProductRecipeViewSet(viewsets.ModelViewSet):
    """
    Retseptlar tarkibini bevosita boshqarish ViewSet (Faqat Administrator uchun).
    """
    permission_classes = [IsAdminRole]
    serializer_class = ProductRecipeSerializer
    filterset_fields = ['product', 'ingredient']

    def get_queryset(self):
        return get_recipes_queryset()
