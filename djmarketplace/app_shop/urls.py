from django.urls import path
from django.views.decorators.cache import cache_page

from app_shop.views import *

urlpatterns = [
    path('', MaimPageView.as_view(), name='main'),
    path('shop_list/', ShopListView.as_view(), name='shop_list'),
    path('shop_list/<slug:slug>/', ShopListView.as_view(), name='shop_list_category'),
    path('shop_list/<slug:slug>/detail/', cache_page(60 * 60)(ShopDetailView.as_view()), name='shop_detail'),
    path('discount_list/', DiscountListView.as_view(), name='discount'),
    path('discount_list/<slug:slug>/', DiscountListView.as_view(), name='discount_category'),
    path('top_sale/', TopSaleListView.as_view(), name='top_sale'),
    path('new_item_list/', NewItemListView.as_view(), name='new_item'),
    path('new_item_list/<slug:slug>/', NewItemListView.as_view(), name='new_item_category'),
    path('shop/<slug:shop_slug>/item/<int:pk>/detail/', ItemDetailView.as_view(), name='item_detail'),

]
