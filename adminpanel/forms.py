from django.forms import ModelForm
from django import forms
from django.shortcuts import get_object_or_404
from django.contrib import messages
from users.models import Payment, Profile
from django.utils import timezone
from django.core.exceptions import ValidationError


class PaymentForm(forms.ModelForm):
    profile_phone = forms.IntegerField(label='Phone')
    amount = forms.DecimalField(min_value=0, label='Amount')
    expiry_date= forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = Payment
        fields = ['profile_phone','amount','expiry_date','status','subscription']

    def clean_profile_phone(self):
        profile_phone = self.cleaned_data['profile_phone']
        if not str(profile_phone).startswith('9'):
            raise ValidationError('Phone number must start with 9.')
        if len(str(profile_phone)) != 10:
            raise ValidationError('Phone number must be 10 digits.')
        return profile_phone

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise ValidationError('Amount must be a positive number.')
        return amount

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        now = timezone.now()
        if expiry_date <= now + timezone.timedelta(days=1):
            raise ValidationError('Expiration date must be more than a day from now.')
        return expiry_date