from django.urls import path

from app_cart.views import *

urlpatterns = [
    path('', CartDetailView.as_view(), name='detail_cart'),
    path('add/<int:pk>/', CartAddItem.as_view(), name='add'),
    path('update/<int:pk>/', CartUpdateItem.as_view(), name='update'),
    path('remove/<int:pk>/', CartRemoveItem.as_view(), name='cart_remove'),
]