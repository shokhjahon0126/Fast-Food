from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.orders.views import (
    CustomerOrderViewSet,
    CashierOrderViewSet,
    TelegramOrderCreateView,
)

router = DefaultRouter()
router.register(r'my-orders', CustomerOrderViewSet, basename='customer-order')
router.register(r'cashier', CashierOrderViewSet, basename='cashier-order')

urlpatterns = [
    path('telegram-order/', TelegramOrderCreateView.as_view(), name='telegram-order-create'),
    path('', include(router.urls)),
]

