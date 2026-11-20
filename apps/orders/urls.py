from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.orders.views import CustomerOrderViewSet, CashierOrderViewSet

router = DefaultRouter()
router.register(r'my-orders', CustomerOrderViewSet, basename='customer-order')
router.register(r'cashier', CashierOrderViewSet, basename='cashier-order')

urlpatterns = [
    path('', include(router.urls)),
]

