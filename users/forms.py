from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError

def validate_ten_digits(value):
    if len(str(value)) != 10:
        raise ValidationError('Phone number must be exactly 10 digits long.')


class CustomUserCreationForm(UserCreationForm):
    phone = forms.IntegerField(
        validators=[validate_ten_digits],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'name': 'phone',
                'placeholder': 'phone..',
                'pattern': r'9[78][0-9]{8}',
                'title': 'Phone number should start with 9, second digit should be 7 or 8, and the remaining digits should be any digit from 0 to 9'
            }
        )
    )
    
    class Meta:
        model = User
        fields = ['username','email', 'phone','password1','password2']

    def  __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, *kwargs)

        for name,field in self.fields.items():
            print(field.label)
            field.widget.attrs.update({'class':'input'})

    # username = forms.CharField(
    # max_length=150,
    # widget=forms.TextInput(attrs={'placeholder': 'Username'})
    # )
    # email = forms.EmailField(
    #     widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    # )
    # password1 = forms.CharField(
    #     widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    # )
    # password2 = forms.CharField(
    #     widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    # )
    