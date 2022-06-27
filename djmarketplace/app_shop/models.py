from decimal import Decimal
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from app_users.models import Profile


class Item(models.Model):
    """ Модель для создания экземпляра товара """
    default_errors = {
        'required': _('This field is required'),
        'invalid': _('Please enter a valid value')
    }

    name = models.CharField(
        max_length=100,
        db_index=True,
        error_messages=default_errors,
        verbose_name=_('item title')
    )
    slug = models.SlugField(
        max_length=100,
        db_index=True
    )
    description = models.TextField(
        blank=True,
        error_messages=default_errors,
        verbose_name=_('item description ')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('create date')
    )
    update_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('update date')
    )
    image = models.ImageField(
        upload_to='item_image/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name=_('item image')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('price')
    )
    discount = models.PositiveIntegerField(
        verbose_name=_('discount')
    )
    stock = models.PositiveIntegerField(
        verbose_name=_('quantity')
    )
    available = models.BooleanField(
        default=True,
        verbose_name=_('available')
    )

    category = models.ForeignKey(
        'ItemCategory',
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name=_('category')
    )
    shop = models.ForeignKey(
        'Shop',
        default=None,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('seller')
    )

    class Meta:
        db_table = 'app_items'
        ordering = ['name']
        verbose_name = _('item')
        verbose_name_plural = _('items')
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    def sale(self) -> float:
        """
        Функция для корректного отображения цены товара
        с учетом всех скидок в панели администратора
        :return: цена товара
        """
        return round((float(str(self.price)) * (100 - float(str(self.discount))) / 100), 2)

    sale.short_description = _('Current price')
    sale.allow_tags = True

    def is_stock(self) -> bool:
        """
         Функция проверяет наличие товара на складе магазина
        :return: True or False
        :rtype: bool
        """

        if int(self.stock) > 0:
            return True
        return False

    def get_current_price(self):
        """
         Функция для получения текущей цены товара
        :return: цена товара
        """
        if self.discount != 0:
            return self.get_sale_price()
        return Decimal(str(self.price))

    def get_sale_price(self):
        """
        Функция для получения цены товара с учетом скидки
        :return: цену товара
        """
        discount = (100 - int(str(self.discount))) / 100
        price = float(str(self.price))
        new_price = round(price * discount, 2)
        return float(new_price)

    def write_off_item(self, item):
        """
        Функция для списания товара со склада магазина
        :param item:
        :return: кол-во товара
        """
        current_stock = self.stock
        current_stock -= item
        self.stock = current_stock
        return self.stock

    def get_absolute_url(self):
        return reverse('app_shop:item_detail', kwargs={'slug': self.slug})


class ItemCategory(models.Model):
    name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_('Category')
    )
    slug = models.SlugField(
        max_length=200,
        db_index=True,
        unique=True
    )
    image = models.ImageField(
        upload_to='item_category/%Y/%m/%d',
        default='static/img/default_category.jpg',
        blank=True,
        null=True,
        verbose_name=_('item image')
    )

    class Meta:
        db_table = 'app_item_category'
        ordering = ('name',)
        verbose_name = _('Item category')
        verbose_name_plural = _('Item categories')

    def __str__(self):
        return self.name


class Shop(models.Model):
    """
    Модель для создания Магазина.
    Связь ('FK') с моделью 'ShopCategory'.
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('Shop name')
    )
    slug = models.SlugField(
        max_length=100,
        db_index=True,
        unique=True,
        null=True
    )
    description = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_('Shop description')
    )
    category = models.ForeignKey(
        'ShopCategory',
        null=True,
        blank=True,
        related_name='shops',
        on_delete=models.CASCADE,
        verbose_name=_('category')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('is active')
    )
    image = models.ImageField(
        upload_to=f'shop_avatar/%Y/%m/%d/',
        default='static/img/default_shop.jpg',
        blank=True,
        null=True,
        verbose_name=_('Shop avatar')
    )

    class Meta:
        db_table = 'app_shop'
        ordering = ('name',)
        verbose_name = _('Shop')
        verbose_name_plural = _('Shops')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('app_shop:shop_detail', kwargs={'slug': self.slug})


class ShopCategory(models.Model):
    """
       Модель для создания категорий магазинов.
       Связь ('FK') с моделью 'Shop'.
    """
    name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_('Shop category')
    )
    slug = models.SlugField(
        max_length=200,
        db_index=True,
        unique=True
    )
    description = models.TextField(
        verbose_name=_('category description '),
        blank=True
    )
    icon = models.ImageField(
        upload_to=f'shop_category/',
        default='static/img/default_category.jpg',
        blank=True,
        null=True,
        verbose_name=_('Shop avatar')
    )

    class Meta:
        db_table = 'app_shop_category'
        ordering = ('name',)
        verbose_name = _('Shop category')
        verbose_name_plural = _('Shop categories')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('app_shop:shop_list_category', kwargs={'slug': self.slug})


@receiver(post_save, sender=Profile)
def create_new_note(instance, **kwargs):
    key = make_template_fragment_key('purchase_story', [instance.user.username])
    cache.delete(key)


class RepostList(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE, verbose_name=_('item'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('quantity item'))

    class Meta:
        db_table = 'app_report_list'
        ordering = ('quantity',)
        verbose_name = _('Sale report')
        verbose_name_plural = _('Sale reports')
