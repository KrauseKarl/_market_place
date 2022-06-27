from django import forms
from app_order.models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'


class StatDateForm(forms.Form):
    start = forms.DateTimeField()
    finish = forms.DateTimeField()


