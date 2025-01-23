# auctions/forms.py

from django import forms
from decimal import Decimal 
from .models import Auction, Lot

class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['title', 'description', 'start_time', 'end_time', 'min_bid_increment']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class LotForm(forms.ModelForm):
    class Meta:
        model = Lot
        fields = ['auction', 'title', 'description', 'start_price', 'category']
        widgets = {
            'auction': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'start_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

class AddBalanceForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=Decimal('0.01'), 
        label='Сумма (KZT)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите сумму'})
    )
# auctions/forms.py

class PlaceBidForm(forms.Form):
    bid_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        label='Сумма ставки',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите сумму'})
    )
