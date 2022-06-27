from django import forms

QUANTITY = [(i, str(i)) for i in range(1, 16)]


class CartAddProductForm(forms.Form):
    """Форма для выбора кол-ва товара для добавления в корзину """
    quantity = forms.TypedChoiceField(choices=QUANTITY, coerce=int, label='quantity')
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
