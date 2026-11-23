from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.products.views import CategoryViewSet, ProductViewSet, ProductRecipeViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'recipes', ProductRecipeViewSet, basename='product-recipe')
router.register(r'products', ProductViewSet, basename='product-alias')
router.register(r'', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]

