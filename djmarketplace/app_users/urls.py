from django.urls import path
from django.views.decorators.cache import cache_page

from app_users.views import *


urlpatterns = [
    path('accounts/login/', UserLoginView.as_view(), name='login'),
    path('accounts/logout/', UserLogoutView.as_view(), name='logout'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/profile/<int:pk>/', ProfileDetailView.as_view(), name='profile'),
    path('accounts/profile_edit/<int:pk>/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('accounts/profile/<int:pk>/recharge_balance/', UpdateBalanceView.as_view(), name='recharge_balance'),
    path('accounts/loyalty_program/', cache_page(60*60)(LoyaltyProgram.as_view()), name='loyalty_program')
    # path('accounts/change-password/', PasswordChangeView.as_view(), name='change_password'),
]