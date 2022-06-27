from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Sum, Q, F
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, TemplateView, CreateView

from app_shop.models import Item
from app_users.models import *
from app_order.models import Order, OrderItem
from app_users.forms import RegisterUserForm, UpdateBalanceForm, UpdateProfileForm, UpdateUserForm
from app_users.models import Profile, User


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_field_name = '/'  # reverse('app_shop:main')


class UserLogoutView(LogoutView):
    template_name = 'accounts/logout.html'


class RegisterUserView(CreateView):
    model = User
    template_name = 'accounts/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('app_shop:main')

    def form_valid(self, form):
        user = form.save()
        verified_user = Group.objects.get(name='verified')
        user.groups.add(verified_user)
        Profile.objects.create(
            user=user,
            avatar=form.cleaned_data.get('avatar'),
            balance=0,
            status='bgn',
        )
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(self.request,
                            username=username,
                            password=raw_password)
        login(self.request, user)
        return redirect('app_shop:main')


class ProfileDetailView(UserPassesTestMixin, PermissionRequiredMixin, DetailView):
    """ Класс-представление для отображения личного кабинета пользователя"""
    model = Profile
    template_name = 'accounts/profile.html'
    paginate_by = 4
    login_url = settings.LOGIN_URL
    permission_required = 'app_users.change_profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_purchases'] = self.total_purchases()
        context['total_quantity'] = context['total_purchases'].count()
        context['discount_items'] = self.discount_items()
        context['offer'] = self.offers()
        context['total_sum'] = self.total_sum()
        context['orders'] = self.orders()

        return context

    def test_func(self):
        """" Проверка на доступ к личной страницы пользователя """
        if self.request.user.is_authenticated:
            if self.request.user.profile == self.get_object():
                return True
            return False
        return False

    def orders(self):
        """Функция для отображения всех заказов пользователя """
        orders = Order.objects.select_related('user').filter(user_id=self.object.id).order_by('-created')
        return orders

    def total_purchases(self):
        """" Функция для отображения всех покупок пользователя """
        total_purchases = OrderItem.objects.select_related('order__user').filter(
            order__user_id=self.object.id).order_by('-quantity')
        return total_purchases

    def discount_items(self):
        """" Функция для отображения товаров со скидкой """

        discount_list = Item.objects.select_related('shop', 'category').filter(
            Q(discount__gt=0) & Q(stock__gt=0) & Q(shop__is_active=True)).order_by('-discount')[:10]

        discounts_cache_key = 'discount:{}'.format(self.object.user_id)
        current_cache = cache.get(discounts_cache_key, discount_list)
        if current_cache != discount_list:
            cache.set(discounts_cache_key, discount_list, 60)

        return discount_list

    def offers(self):
        """" Функция для отображения специальных предложений """

        purchase_list = self.total_purchases()

        if purchase_list:
            favorite_cat = purchase_list
            favorite_cat = favorite_cat[0].product.category
            offers_list = Item.objects.select_related('shop', 'category').filter(
                Q(category=favorite_cat) &
                Q(stock__gt=0) &
                Q(shop__is_active=True)).order_by('price')[:5]
            current_cache = cache.get('favorites:{}'.format(self.object.user_id), offers_list)
            if current_cache != offers_list:
                favorites_key_cache = 'favorites:{}'.format(self.object.user_id)
                cache.set(favorites_key_cache, offers_list, 60)

            return offers_list

        return None

    def total_sum(self):
        """"
        Функция для подсчета суммы, потраченной пользователем и
        проверки (обновления) его текущего статуса в программе лояльности
        """

        total_sum = OrderItem.objects.select_related('order__user').filter(order__user_id=self.object.id).order_by(
            '-quantity').aggregate(total=Sum(F('price') * F('quantity')))['total']
        current_status = self.object.status
        if total_sum:
            if total_sum < 5000:  # SCORE_EXT_STS = 10000 $
                need_sum_to_update = round(5000 - float(total_sum))
            else:
                if 10000 > total_sum >= 5000:
                    self.object.status = 'adv'
                    need_sum_to_update = round(10000 - float(total_sum))
                else:
                    self.object.status = 'exp'
                    need_sum_to_update = False
                if current_status != self.object.status:
                    self.object.save()

            return {'sum': round(total_sum,2), 'need_sum_to_update': round(need_sum_to_update, 0)}

        return 0


class UpdateBalanceView(PermissionRequiredMixin, UpdateView):
    """ Класс-представление для пополнения баланса пользователя"""
    model = Profile
    form_class = UpdateBalanceForm
    template_name = 'accounts/recharge_balance.html'
    context_object_name = 'profile'
    permission_required = ('app_users.change_profile', 'app_users.view_profile')

    def test_func(self):
        """" Проверка на доступ к личной страницы пользователя """
        if self.request.user.is_authenticated:
            if self.request.user.profile == self.get_object():
                return True
            return False
        return False

    def form_valid(self, form):
        """" Функция для пополнения баланса пользователя """
        user = self.get_object()
        new_sum = form.cleaned_data['balance']
        if new_sum > 0:
            user.balance = F('balance') + new_sum
            user.save()
            return redirect('app_users:profile', user.pk)
        return redirect('app_users:recharge_balance', user.pk)


class LoyaltyProgram(TemplateView):
    """Представление-класс для отображения программы лояльности"""
    model = Profile
    template_name = 'accounts/loyalty_program.html'


class ProfileUpdateView(UserPassesTestMixin, PermissionRequiredMixin, UpdateView):
    """ Класс-представление для обновления информации о пользователи"""
    model = Profile
    second_model = User
    form_class = UpdateProfileForm
    second_form_class = UpdateUserForm
    template_name = 'accounts/profile_edit.html'
    context_object_name = 'profile'
    permission_required = 'app_users.change_profile'
    login_url = settings.LOGIN_URL

    def test_func(self):
        """" Проверка на доступ к личной страницы пользователя """
        if self.request.user.is_authenticated:
            if self.request.user.profile == self.get_object():
                return True
            return False
        return False

    def get_success_url(self):
        return redirect('app_users:profile', pk=self.get_object().user.profile.pk)

    def get_context_data(self, **kwargs):
        """
        Функция для добавления дополнительной формы,
        для обновления экземпляра расширенной модели пользователя ('Profile')
        """
        kwargs['user_form'] = self.second_form_class()
        kwargs['profile_form'] = self.get_form()
        return kwargs

    def get(self, request, *args, **kwargs):
        """ Функция-get для отображения чистой формы для новых данных о пользователе"""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """ Функция-post для отправки обновленных данных о пользователе"""
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            return self.get_success_url()
        else:
            context = {'user_form': user_form, 'profile_form': profile_form}
            return render(request, 'accounts/profile_edit.html', context)
