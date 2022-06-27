from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    """ Модель для создания расширенного профиля пользователя.
        Связь ('O2O') с моделью 'User'.
    """
    LOYALTY_STATUS = [  # уровни программы лояльности
        ('bgn', _('beginner')),
        ('adv', _('advanced')),
        ('ext', _('expert')),
    ]

    SCORE_ADV_STS = 5000  # сумма необходимая для  статуса 'advanced'
    SCORE_EXT_STS = 10000  # сумма необходимая для  статуса 'expert'
    QUOTE = 80  # курс 1 USD = 80 RUB

    default_errors = {
        'required': _('This field is required'),
        'invalid': _('Please enter a valid value')
    }

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        error_messages=default_errors
    )
    verified_id = models.BooleanField(
        default=False,
        verbose_name=_('Verified user')
    )
    avatar = models.ImageField(
        upload_to='profile/%Y/%m/%d',
        default='static/img/default_profile.jpg',
        blank=True,
        null=True,
        verbose_name=_('Avatar')
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Balance')
    )
    status = models.CharField(
        max_length=3,
        choices=LOYALTY_STATUS,
        default='bgn',
        verbose_name=_('Loyalty status')
    )

    class Meta:
        db_table = 'app_profile'
        ordering = ['user']
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return f'{self.user}'

    def get_balance(self) -> float:
        """Функция возвращает текущий баланс пользователя"""
        return round(float(self.balance), 2)

    def profile_status(self):
        """ Функция возвращает текущий статус пользователя """

        if self.verified_id:
            return _('Verified Profile')
        return _('Confirmation required')

    def profile_moderated(self) -> bool:
        """ Функция для изменения(верификации)  статуса пользователя """

        self.verified_id = True
        return self.verified_id

    def get_customer(self):
        new_group = Group.objects.get(name='customer')
        user = self.user.groups.add(new_group)
        return user

    def check_loyalty_status(self, total_sum=None) -> str:
        """
        Функция для проверки и обновления статуса
        пользователя в программе лояльности
        """

        if total_sum >= self.SCORE_EXT_STS:
            self.status = 'ext'
        elif total_sum >= self.SCORE_ADV_STS:
            self.status = 'adv'
        else:
            self.status = 'bgn'
        return self.status

    def personal_discount(self, price):
        """
       Функция для подсчета персональной скидки
       пользователя
        """
        if self.status == 'ext':
            price *= 0.95
        elif self.status == 'adv':
            price *= 0.97
        else:
            price *= 1

        return price

    def write_off_money(self, money: float) -> float:
        """
        Функция для списания денежных средств
        с баланса пользователя при покупки товара
        """
        curr_balance = float(self.balance)
        curr_balance -= money
        self.balance = round(curr_balance, 2)
        return curr_balance

    def get_absolute_url(self):
        return reverse('app_users:profile', kwargs={'pk': self.pk})


@receiver(post_save, sender=Profile)
def create_update_note(instance, **kwargs):
    """
    Функция для обновления cache в случае изменения данных на странице пользователя
    :param instance:
    :param kwargs:
    :return:
    """
    key = make_template_fragment_key('profile_info', [instance.user.profile])
    cache.delete(key)


@receiver(post_save, sender=Profile)
def create_new_profile(instance, **kwargs):
    """
      Функция для обновления cache в случае изменения данных пользователя в navbar
      :param instance:
      :param kwargs:
      :return:
      """
    key = make_template_fragment_key('profile', [instance.user.profile])
    cache.delete(key)
