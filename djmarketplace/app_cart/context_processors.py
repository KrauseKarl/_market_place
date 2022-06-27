from app_cart.cart import Cart


def cart(request):
    """Функция для добавление контекстных данных корзины на все страницы сайта"""
    return {'app_cart': Cart(request)}