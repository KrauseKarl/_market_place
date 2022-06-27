from django.urls import path

from app_order.views import OrderCreateView, OrderReportDetail, OrderDetail

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('order_statistic/', OrderReportDetail.as_view(), name='order_statistic'),
    path('order_detail/<int:pk>/',  OrderDetail.as_view(), name='order_detail'),
]
