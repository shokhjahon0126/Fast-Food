from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.inventory.views import IngredientViewSet, SupplyViewSet

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'supplies', SupplyViewSet, basename='supply')

urlpatterns = [
    path('', include(router.urls)),
]

