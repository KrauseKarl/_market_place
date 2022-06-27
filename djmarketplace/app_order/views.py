from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin, LoginRequiredMixin
from django.utils.timezone import now
from django.db.models import Sum
from django.shortcuts import render
from django.db import transaction
from django.views import View
from django.views.generic import CreateView, DetailView

from app_shop.models import *
from app_order.models import *
from app_order.forms import *
from app_cart.cart import Cart


class OrderCreateView(LoginRequiredMixin, CreateView):
    """ Класс-представление для создания заказа и оплаты товаров"""
    model = Order
    template_name = 'app_order/new_order.html'
    form_class = OrderCreateForm
    login_url = settings.LOGIN_URL
    permission_required = ('app_order.create_order', 'app_order.view_order')

    def get_context_data(self, **kwargs):
        kwargs['form'] = self.get_form()
        kwargs['cart'] = Cart(self.request)

        return kwargs

    def get(self, request, *args, **kwargs):
        """Функция-get для отображения формы."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """
        Функция-post для покупки товаров из корзины.
        Создает объект(запись) ('Order')
        Создает объект ('OrderItem')
        Создает объект(запись) ('Report List)
        Списывает денежные средства с баланса пользователя('Profile')
        Списывает кол-во единиц купленного товара на складе('Item')
        в случае успешной транзакции
        :return: оформленный заказом
        в обратном случае
        :return: оформленный заказом
        корзину с товарами, форму и сообщение об ошибки(недостаточно средств)
        :rtype: dict
        """

        cart = Cart(request)
        form = self.get_form()
        user = self.request.user.profile
        user_balance = user.get_balance()
        total_cost = cart.get_total_price()
        if total_cost <= user_balance:
            if form.is_valid():
                order = form.save()
                order_list = []
                for item in cart:
                    with transaction.atomic():
                        product = item['product']
                        price = item['price']
                        quantity = item['quantity']
                        order_list.append(OrderItem(
                            order=order,
                            product=product,
                            price=price,
                            quantity=quantity))
                        report, create = RepostList.objects.get_or_create(item=product, quantity=quantity)

                        report.save()
                        product.write_off_item(quantity)
                        product.save()
                        total = float(item['total_price'])
                        user.write_off_money(total)
                        user.save()
                OrderItem.objects.bulk_create(order_list)
                cart.clear()
                return render(request, 'app_order/success_creation.html',
                              {'order': order})
            else:
                context = {'cart': cart, 'form': form}
                return render(request, 'app_order/new_order.html', context)
        else:
            context = {'cart': cart, 'form': form, 'message': 'not enough money to pay, pls, recharge your balance'}
            return render(request, 'app_order/new_order.html', context)


class OrderDetail(DetailView):
    """ Класс-представление для отображения заказа пользователя"""
    model = Order
    template_name = 'app_order/order_detail.html'
    paginate_by = 4
    login_url = settings.LOGIN_URL

    # permission_required = ('app_order.change_order', 'app_order.view_order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        context['items'] = OrderItem.objects.select_related('order').filter(order_id=order.id)
        return context

    # def test_func(self):
    #     """" Проверка на доступ к личной страницы пользователя """
    #
    #     if self.request.user.profile == self.get_object():
    #         return True
    #     return False


class OrderReportDetail(View):
    """
    Класс-представление для создания отчёт по наиболее
    продаваемым товарам за период времени
    """
    model = Order
    template_name = 'app_order/order_statistic.html'
    paginate_by = 4

    def get(self, request):
        """
         Функция для GET-запроса. Возвращает форму для ввода временного периода.

        :return: форма, сообщение о выборе периода(об отсутствии проданных товаров за период времени)
        :rtype:dict
        """
        form = StatDateForm()
        return render(request, 'app_order/order_statistic.html', {'form': form, 'nothing': True})

    def post(self, request, *args, **kwargs):
        """
        Функция для POST-запроса.  Возвращает список проданных  за период времени

        в случае корректных данных:
        :return: форму, список проданных товаров, временное промежуток
        в противном случае:
        :return: форма, сообщение об ошибки(некорректный период)
        :rtype:dict
        """
        form = StatDateForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data.get('start')
            finish = form.cleaned_data.get('finish')
            today = now()
            if start <= finish <= today:
                items = OrderItem.objects.values('product__name', 'product__id', 'product__image'). \
                    filter(order__created__range=(start, finish)). \
                    annotate(Sum('quantity')).order_by('-quantity__sum')
                context = {'others': items, 'form': form, 'date': {'start': start, 'finish': finish}}
                return render(request, 'app_order/order_statistic.html', context)
            else:
                context = {'message': 'error'}
                return render(request, 'app_order/order_statistic.html', context)
        else:
            return render(request, 'app_order/order_statistic.html', {'form': form, 'nothing': 1})
