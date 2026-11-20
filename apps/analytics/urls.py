from django.urls import path
from apps.analytics.views import (
    DashboardOverviewView,
    ProductSalesRankingView,
    SalesTrendView,
)

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', DashboardOverviewView.as_view(), name='dashboard-overview'),
    path('products-ranking/', ProductSalesRankingView.as_view(), name='products-ranking'),
    path('sales-trend/', SalesTrendView.as_view(), name='sales-trend'),
]
