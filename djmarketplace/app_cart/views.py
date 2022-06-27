from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, DetailView, UpdateView

from app_shop.models import Item
from app_cart.cart import Cart
from app_cart.forms import CartAddProductForm


class CartAddItem(View):
    """ Класс-представление для создания корзины с товарами"""
    model = Item
    template_name = 'app_shop/item_detail.html'

    @staticmethod
    def post(request, *args, **kwargs):
        """
         Функция-post для создания корзины.
         Создает объект(запись) ('Cart')
         возвращает на страницу товара.
         в случае успешного добавления товара
         :return: форму, товар и сообщение об успешном добавлении
         в обратном случае
         :return: форму товар и сообщение об ошибки(недостаточно ед. товара)
         :rtype: dict
         """
        cart = Cart(request)
        pk = kwargs['pk']
        item = get_object_or_404(Item, id=pk)
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if item.stock >= quantity:
                cd = form.cleaned_data
                cart.add(product=item,
                         quantity=quantity,
                         update_quantity=cd['update'])
                return render(request, 'app_shop/item_detail.html',
                              {'form': form, 'item': item, 'message': "successful added to cart"})
            return render(request, 'app_shop/item_detail.html',
                          {'form': form, 'item': item, 'message': "lack of the product"})


class CartUpdateItem(UpdateView):
    """ Класс-представление для обновления кол-ва товаров в корзине"""
    model = Item
    template_name = 'app_cart/detail_cart.html'

    def post(self, request, *args, **kwargs):
        """
        Функция-post для обновления кол-ва товара в корзине.
        :return: возвращает на страницу корзины
        :rtype: dict
        """
        cart = Cart(request)
        pk = kwargs['pk']
        item = get_object_or_404(Item, id=pk)
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if item.stock >= quantity:
                cd = form.cleaned_data
                cart.update(
                    product=item,
                    quantity=quantity,
                    update_quantity=cd['update']
                )
                return redirect('app_cart:detail_cart')


class CartRemoveItem(TemplateView):
    """ Класс-представление для удаления товара из корзины"""
    model = Item
    template_name = 'app_shop/item_detail.html'

    def get(self, request, *args, **kwargs):
        """
              Функция-get для удаления товара из корзине.
              :return: возвращает на страницу корзины
              :rtype: dict
              """
        pk = kwargs['pk']
        cart = Cart(request)
        product = get_object_or_404(Item, id=pk)
        cart.remove(product)
        return redirect('app_cart:detail_cart')


class CartDetailView(DetailView):
    """ Класс-представление для отображения корзины корзины"""

    model = Item
    template_name = 'app_cart/cart_detail.html'

    def get(self, request, *args, **kwargs):
        """
        Функция-get для отображения корзины.
        возвращает на страницу корзины
        :return: корзину и id пользователя
        :rtype: dict
        """
        cart = Cart(request)
        user = request.user
        for item in cart:
            item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'],
                                                                       'update': True})
        context = {'cart': cart, 'user': user}
        return render(request, 'app_cart/cart_detail.html', context)

