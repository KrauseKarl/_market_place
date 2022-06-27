from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from app_users.models import Profile
from django.utils.translation import gettext_lazy as _


class AuthForm(forms.Form):
    """
    Форма для регистрации нового пользователя
    (model User)
    """
    default_errors = {
        'required': _('This field is required'),
        'invalid': _('Please enter a valid value')
    }
    username = forms.CharField(error_messages=default_errors)
    password = forms.CharField(widget=forms.PasswordInput, error_messages=default_errors)


class RegisterUserForm(UserCreationForm):
    """
    Форма для регистрации нового пользователя
    (model Profile)
    """
    default_errors = {
        'required': _('This field is required'),
        'invalid': _('Please enter a valid value')
    }
    username = forms.CharField(
        max_length=30,
        label=_('Username'),
        error_messages=default_errors,
        widget=forms.Textarea(attrs={'rows': 1, 'cols': 20})
    )
    first_name = forms.CharField(
        max_length=30,
        label=_('First name'),
        widget=forms.Textarea(attrs={'rows': 1, 'cols': 20})
    )
    last_name = forms.CharField(
        max_length=30,
        label=_('Last name'),
        widget=forms.Textarea(attrs={'rows': 1, 'cols': 20})
    )
    password1 = forms.CharField(
        label=_("password"),
        strip=False,
        help_text='Your password must contain at least: '
                  ' 1 uppercase letter,  '
                  ' 1 lowercase letter,'
                  ' 1 special character (#?!@$%^&*-), '
                  ' 1 number and  8 characters.',
        error_messages=default_errors,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )
    password2 = forms.CharField(
        label=_("Confirm password"),
        strip=False,
        help_text='',
        error_messages=default_errors,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )
    avatar = forms.ImageField(
        required=False,
        label=_('avatar')
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2', 'avatar',)


class UpdateUserForm(forms.ModelForm):
    """
    Форма для обновления полей 'First name' и 'Last name'
    профиля пользователя (model User)
    """
    default_errors = {
        'required': _('This field is required'),
        'invalid': _('Please enter a valid value')
    }
    first_name = forms.CharField(
        max_length=30,
        label=_('First name'),
        widget=forms.Textarea(attrs={'rows': 1, 'cols': 20}),
        error_messages=default_errors
    )
    last_name = forms.CharField(
        max_length=30,
        label=_('Last name'),
        error_messages=default_errors,
        widget=forms.Textarea(attrs={'rows': 1, 'cols': 20})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class UpdateProfileForm(forms.ModelForm):
    """
    Форма для обновления полей
    'avatar' профиля пользователя
    (model Profile)
    """
    my_default_errors = {
        'required': _('This field is required'),
        'invalid': _('Please enter a valid value')
    }
    avatar = forms.ImageField(
        required=False,
        label=_('avatar')
    )

    class Meta:
        model = Profile
        fields = ['avatar']


class UpdateBalanceForm(forms.ModelForm):
    """
    Форма для обновления полей
    'balance' профиля пользователя
    (model Profile)
    """

    class Meta:
        model = Profile
        fields = ('balance',)


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    email = forms.EmailField(max_length=254, help_text='Enter a valid email address')

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]
