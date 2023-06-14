import django_filters
from django_filters import DateFilter,CharFilter
from django import forms
from users.models import Payment, Profile

class PaymentFilter(django_filters.FilterSet):
    payment_start_date = DateFilter(field_name="payment_date",
        lookup_expr='gt',
        label='Payment Start Date',
        widget=forms.DateInput(attrs={
            'placeholder': 'Select a start date',
            'type': 'date'
        })
    )
    payment_end_date = DateFilter(field_name="payment_date",
        lookup_expr='lt',
        label='Payment End Date',
        widget=forms.DateInput(attrs={
            'placeholder': 'Select an end date',
            'type': 'date'
        })
    )

    expiration_start_date = DateFilter(field_name="expiry_date",
        lookup_expr='gt',
        label='Expiration Start Date',
        widget=forms.DateInput(attrs={
            'placeholder': 'Select a start date',
            'type': 'date'
        })
    )
    expiration_end_date = DateFilter(field_name="expiry_date",
        lookup_expr='lt',
        label='Expiration End Date',
        widget=forms.DateInput(attrs={
            'placeholder': 'Select an end date',
            'type': 'date'
        })
    )

    phone = django_filters.NumberFilter(
        field_name="profile__phone",
        label='Phone Number',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter phone number',
            'type': 'number',
        })
    )

    status = django_filters.ChoiceFilter(
        field_name="status",
        label='Status',
        choices=(('active', 'Active'), ('expired', 'Expired')),
        empty_label='All',
        widget=forms.Select(attrs={
            'placeholder': 'Select status',
        })
    )


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
        })
    ) 

    username = django_filters.CharFilter(
        field_name="username",
        label='Username',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter username',
            'type': 'Text',
        })
    )


    class Meta:
        model = Profile
        fields = ['phone','username']
