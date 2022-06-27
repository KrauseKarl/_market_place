from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404
from django.core.cache import cache
from django.db.models import Q
from django.views.generic import ListView, CreateView, DetailView, TemplateView


from app_cart.forms import CartAddProductForm
from app_order.forms import OrderCreateForm
from app_order.models import OrderItem
from app_shop.models import Item, ItemCategory, Shop, ShopCategory, RepostList


class MixinPaginator(Paginator):
    def my_paginator(self, queryset, request, paginate_by):
        try:
            page = int(request.GET.get('page', '1'))
        except:
            page = 1
        paginator = Paginator(queryset, paginate_by)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)
        return queryset


class MaimPageView(TemplateView):
    """Представление-класс для отображения главной страницы"""

    template_name = 'app_shop/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['discount_items'] = self.discount_items()
        context['new_items'] = self.new_items()
        context['top_sale_items'] = self.top_sale_items()
        context['shops'] = self.shops()
        return context

    def discount_items(self):
        discount_items = Item.objects.select_related('shop__category', 'category').filter(
            Q(discount__gt=0) & Q(stock__gt=0)).order_by('-discount')[:6]
        cache.get_or_set('discount', discount_items, 60)
        return discount_items

    def new_items(self):
        new_items = Item.objects.select_related('shop__category', 'category').exclude(
            discount__gt=0).filter(
            stock__gt=0).order_by('-created_at')[:6]
        cache.get_or_set('new_items', new_items, 60)

        return new_items

    def top_sale_items(self):
        top_sale_items = RepostList.objects.select_related('item__category', 'item__shop__category').filter(
            item__stock__gt=0).order_by('-quantity')[:6]
        cache.get_or_set('top_sale_items', top_sale_items, 60)

        return top_sale_items

    def shops(self):
        shops = Shop.objects.select_related('category').filter(is_active=True)[:6]
        cache.get_or_set('shops', shops, 60)
        return shops


class ShopListView(ListView, MixinPaginator):
    """Представление-класс для отображения списка магазинов"""

    model = Shop
    paginate_by = 4
    template_name = 'app_shop/shop_list.html'
    context_object_name = 'shops'
    queryset = Shop.objects.select_related('category').filter(is_active=True)
    extra_context = {'categories': ShopCategory.objects.all(), }

    def get(self, request, *args, slug=None):
        categories = ShopCategory.objects.filter(shops__is_active=1).annotate(Count('shops'))
        if slug:
            category = get_object_or_404(ShopCategory, slug=slug)
            shops = Shop.objects.filter(category=category.id)
        else:
            shops = self.queryset
        page_obj = self.my_paginator(shops, self.request, self.paginate_by)
        context = {
            'page_obj': page_obj,
            'shops': shops,
            'categories': categories,
        }
        return render(request, 'app_shop/shop_list.html', context)


class ShopDetailView(DetailView, MixinPaginator):
    """Представление-класс для отображения одного магазина"""

    model = Shop
    context_object_name = 'shop'
    slug_url_kwarg = 'slug'
    template_name = 'app_shop/shop_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = Item.objects.select_related('shop__category', 'category').filter(shop_id=self.get_object().id)
        items = self.my_paginator(items, self.request, 3)
        context['page_obj'] = items

        return context


class DiscountListView(ListView, MixinPaginator):
    """Представление-класс для отображения списка товаров со скидкой"""
    model = Item
    paginate_by = 4
    template_name = 'app_shop/discount.html'
    context_object_name = 'discounts'
    queryset = Item.objects.select_related('shop__category', 'category').filter(
        Q(discount__gt=0) & Q(stock__gt=0) & Q(shop__is_active=True)).order_by('-discount')
    discount_cache_key = 'discounts_{}'.format(context_object_name)
    cache.get_or_set(discount_cache_key, queryset, 30 * 60)

    def get(self, request, *args, slug=None):
        """Функция для сортировки товаров по лучшей скидки, меньшей цене"""
        categories = {
            'max': _('discounts'),
            'min': _('best price'),
            'five': _('discount < 5%'),
            'ten': _('discount < 10%'),
            'more_ten': _('discount > 10%')
        }
        discounts = Item.objects.select_related('shop__category', 'category')
        if slug == 'max':
            discounts = discounts.filter(discount__gt=0).order_by('-discount')
            category = _('Best discount items')
        elif slug == 'min':
            discounts = discounts.filter(discount__gt=0).order_by('price')
            category = _('Best price')
        elif slug == 'five':
            discount = discounts.filter(Q(discount__gt=1) & Q(discount__lt=6)).order_by('discount')
            category = _('discount up to 5%')
        elif slug == 'ten':
            discounts = discounts.filter(Q(discount__gt=5) & Q(discount__lt=11)).order_by('discount')
            category = _('discount up to 10%')
        elif slug == 'more_ten':
            discounts = discounts.filter(discount__gt=11).order_by('-discount')
            category = _('discount more over 10%')
        else:
            discounts = discounts.filter(discount__gt=0).order_by('-created_at')
            category = _('all items')
        page_obj = self.my_paginator(discounts, self.request, self.paginate_by)
        context = {'page_obj': page_obj, 'category': category, 'categories': categories}
        return render(self.request, 'app_shop/discount.html', context)


class TopSaleListView(ListView):
    """Представление-класс для отображения топовых товаров"""

    model = RepostList
    paginate_by = 5
    template_name = 'app_shop/top_sale.html'
    context_object_name = 'tops'
    queryset = RepostList.objects.select_related('item__shop__category').filter(item__stock__gt=0).order_by('-quantity')


class NewItemListView(ListView, MixinPaginator):
    """Представление-класс для отображения списка новых товаров"""

    model = Item
    paginate_by = 8
    template_name = 'app_shop/new_item.html'
    context_object_name = 'items'
    items_cache_key = 'items_{}'.format(context_object_name)
    queryset = Item.objects.select_related('shop__category', 'category').filter(
        Q(stock__gt=0, shop__is_active=True)).order_by('-created_at')
    cache.get_or_set(items_cache_key, queryset, 30 * 60)

    def get(self, request, *args, slug=None):
        """Функция для сортировки товаров по категориям"""

        category = None
        categories = ItemCategory.objects.filter(items__stock__gt=0).annotate(Count('items'))
        print(categories)
        if slug:
            category = get_object_or_404(ItemCategory, slug=slug)
            items = Item.objects.filter(category=category.id)
        else:
            items = self.queryset
        page_obj = self.my_paginator(items, self.request, self.paginate_by)
        context = {'page_obj': page_obj, 'category': category, 'categories': categories}
        return render(request, 'app_shop/new_item.html', context)


class ItemDetailView(DetailView, CreateView):
    """Представление-класс для отображения одного товара"""
    model = Item
    context_object_name = 'item'
    template_name = 'app_shop/item_detail.html'
    form_class = CartAddProductForm

    def get_context_data(self, **kwargs):
        kwargs['form'] = CartAddProductForm
        kwargs['item'] = Item.objects.select_related('shop__category', 'category').get(pk=self.get_object().id)

        return kwargs

    def get(self, request, *args, **kwargs):
        """Функция-get для отображения формы."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        return redirect('app_shop:item_detail', request)
