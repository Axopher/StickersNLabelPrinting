from django.forms import ModelForm
from django import forms
from django.shortcuts import get_object_or_404
from django.contrib import messages
from users.models import Payment, Profile

class PaymentForm(forms.ModelForm):
    profile_phone = forms.IntegerField(label='Phone')
    expiry_date= forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = Payment
        fields = ['profile_phone','amount','expiry_date','status','subscription']
