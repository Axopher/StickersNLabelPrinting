from django import forms
from .models import LabelConfig

class LabelConfigForm(forms.ModelForm):
    text_color_line1 = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))
    text_color_line2 = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))
    text_color_line3 = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))
    text_color_line4 = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))
    class Meta:
        model = LabelConfig
        fields = '__all__'
        exclude = ['user']
