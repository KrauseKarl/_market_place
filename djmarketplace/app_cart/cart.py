from decimal import Decimal
from django.conf import settings

from app_cart.forms import CartAddProductForm
from app_shop.models import Item


class Cart(object):
    """ Класс для создания и управления корзиной."""

    def __init__(self, request):
        """ Инициализируем корзину."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """ Функция для добавления продукта в корзину или обновления его количество."""
        product_id = str(product.id)
        if product_id not in self.cart:
            price = product.get_current_price()
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def update(self, product, quantity, update_quantity=False):
        """ Функция для обновления количества продукта."""
        product_id = str(product.id)
        if product_id in self.cart:
            price = product.get_current_price()
            self.cart[product_id] = {'quantity': quantity,
                                     'price': str(price)}
        self.save()

    def save(self):
        """ Функция для обновление сессии cart."""
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product):
        """Удаление товара из корзины."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """ Перебор элементов в корзине и получение продуктов из базы данных."""
        product_ids = self.cart.keys()

        products = Item.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """ Функция для подсчет всех товаров в корзине."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """ Функция для подсчет стоимости товаров в корзине."""
        return sum(Decimal(item['price']) * item['quantity'] for item in
                   self.cart.values())

    def clear(self):
        """Функция для удаление корзины из сессии."""
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
