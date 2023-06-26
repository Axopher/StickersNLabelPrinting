import django_filters
from django_filters import DateFilter,CharFilter
from django import forms
from users.models import Payment, Profile
from django_filters import ChoiceFilter, FilterSet
from users.models import Subscription

class PaymentFilter(django_filters.FilterSet):
    payment_start_date = DateFilter(field_name="payment_date",
        lookup_expr='gt',
        label='Payment Start Date',
        widget=forms.DateInput(attrs={
            'placeholder': 'Select a start date',
            'type': 'date',
            'class':'form-control',
        })
    )
    payment_end_date = DateFilter(field_name="payment_date",
        lookup_expr='lt',
        label='Payment End Date',
        widget=forms.DateInput(attrs={
            'placeholder': 'Select an end date',
            'type': 'date',
            'class':'form-control',
        })
    )

    expiration_start_date = DateFilter(field_name="expiry_date",
        lookup_expr='gt',
        label='Expiration Start Date',
        widget=forms.DateInput(attrs={
            'placeholder': 'Select a start date',
            'type': 'date',
            'class':'form-control',
        })
    )
    expiration_end_date = DateFilter(field_name="expiry_date",
        lookup_expr='lt',
        label='Expiration End Date',
        widget=forms.DateInput(attrs={
            'placeholder': 'Select an end date',
            'type': 'date',
            'class':'form-control',
        })
    )

    phone = django_filters.NumberFilter(
        field_name="profile__phone",
        label='Phone Number',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter phone number',
            'type': 'number',
            'class':'form-control',
        })
    )

    status = django_filters.ChoiceFilter(
        field_name="status",
        label='Status',
        choices=(('active', 'Active'), ('expired', 'Expired')),
        empty_label='All',
        widget=forms.Select(attrs={
            'placeholder': 'Select status',
            'class':'form-control',
        })
    )

    subscription = django_filters.ChoiceFilter(
        field_name="subscription__plan",
        label='Subscription plan',
        empty_label='All',
        choices=[],
        widget=forms.Select(attrs={
            'placeholder': 'All',
            'class':'form-control',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        subscription_choices = Subscription.objects.values_list('plan', 'plan')
        self.filters['subscription'].extra['choices'] = subscription_choices

    class Meta:
        model = Payment
        fields = ['phone','subscription', 'status']


class ProfileFilter(django_filters.FilterSet):  
    phone = django_filters.NumberFilter(
        field_name="phone",
        label='Phone Number',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter phone number',
            'type': 'number',
            'class':'form-control',
        })
    ) 

    username = django_filters.CharFilter(
        field_name="username",
        label='Username',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter username',
            'type': 'Text',
            'class':'form-control',
        })
    )


    class Meta:
        model = Profile
        fields = ['phone','username']
