from django import forms
from .models import LabelConfig
from django.utils.text import camel_case_to_spaces
from django.forms import Select


class BootstrapSelect(Select):
    def __init__(self, attrs=None, choices=(), **kwargs):
        attrs = attrs or {}
        attrs['class'] = 'form-control'  # Add the Bootstrap class 'form-control'
        super().__init__(attrs, choices, **kwargs)

class LabelConfigForm(forms.ModelForm):
    text_color_line1 = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}),label="Text Color")
    text_color_line2 = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}),label="Text Color")
    text_color_line3 = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}),label="Text Color")
    text_color_line4 = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}),label="Text Color")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget = BootstrapSelect(choices=field.widget.choices)
            else:
                field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = LabelConfig
        fields = '__all__'
        exclude = ['user']
        labels = {

        }

        for field in model._meta.fields:
            field_name = field.name
            if field_name.startswith('font_line') or field_name.startswith('emphasis_line') or \
                    field_name.startswith('text_size_line') or field_name.startswith('text_color_line'):
                label = camel_case_to_spaces(field_name).replace('_line', '').rstrip('1234')
                labels[field_name] = label

                # Add spaces between words and capitalize the label
                label = ' '.join(word.capitalize() for word in label.split('_'))
                labels[field_name] = label