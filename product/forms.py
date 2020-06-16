from django import forms
from .models import *

class AddressForm(forms.ModelForm):
    class Meta:
        model=Address
        exclude = ('user',)
        fields='__all__'


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)

class CheckoutForm(forms.Form):
    house = forms.CharField(required=False)
    street = forms.CharField(required=False)
    landmark = forms.CharField(required=False)
    city = forms.CharField(required=False)
    zip = forms.CharField(required=False)
    mobile =forms.IntegerField(required=False)
    
    
    
    set_address = forms.BooleanField(required=False)
    use_default_address = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

# class CouponForm(forms.Form):
#     code = forms.CharField(widget=forms.TextInput(attrs={
#         'class': 'form-control',
#         'placeholder': 'Promo code',
#         'aria-label': 'Recipient\'s username',
#         'aria-describedby': 'basic-addon2'
#     }))
        