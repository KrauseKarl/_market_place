from datetime import datetime
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from app_shop.models import Item
from app_users.models import Profile


class Order(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile', null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class Meta:
        db_table = 'app_order'
        ordering = ('-created',)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        now = datetime.now()
        return '{} - {}'.format(now.strftime("%d-%m-%Y-%H:%M"), self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_total_quantity(self):
        return sum(item.get_quantity() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Item, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'app_order_item'
        ordering = ('-order',)
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return f'{self.product}'

    def get_quantity(self):
        return self.quantity

    def get_cost(self):
        price = float(str(self.price))
        quantity = float(str(self.quantity))
        total_cost = price * quantity
        return round(total_cost, 2)


@receiver(post_save, sender=Order)
def create_new_note(instance, **kwargs):
    key = make_template_fragment_key('order_story', [instance.user.profile])
    cache.delete(key)
