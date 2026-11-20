from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import (
    CashierViewSet,
    UserProfileView,
    CustomTokenObtainPairView,
    CustomerRegisterView,
)

router = DefaultRouter()
router.register(r'cashiers', CashierViewSet, basename='cashier')

urlpatterns = [
    # Auth & Registration
    path('register/', CustomerRegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),

    # Profile
    path('me/', UserProfileView.as_view(), name='user-profile'),

    # Cashier management (Admin only)
    path('', include(router.urls)),
]
