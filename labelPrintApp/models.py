from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# class StickerForm(models.Model):
#     label_type = models.CharField(max_length=50)
#     per_sheet_dropdown = models.IntegerField()
#     rows_dropdown = models.IntegerField(blank=True, null=True)
#     columns_dropdown = models.IntegerField(blank=True, null=True)
#     csv = models.FileField(upload_to='csv_files/')


from users.models import Profile
from colorfield.fields import ColorField


FONT_CHOICES = [
    ('Courier', 'Courier (fixed-width)'),
    ('Helvetica', 'Helvetica or Arial (sans serif)'),
    ('Times', 'Times (serif)'),
]

EMPHASIS_CHOICES = [
    ('', 'Regular'),
    ('B', 'Bold'),
    ('I', 'Italic'),
    ('U', 'Underline'),
]


# Create your models here.


class LabelConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    font_line1 = models.CharField(max_length=20, choices=FONT_CHOICES, default='helvetica')
    emphasis_line1 = models.CharField(max_length=1, choices=EMPHASIS_CHOICES, default='', blank=True)
    text_size_line1 = models.PositiveIntegerField(default=8)
    text_color_line1 = ColorField(default='#000000')  # ColorField for color picker
    
    font_line2 = models.CharField(max_length=20, choices=FONT_CHOICES, default='helvetica')
    emphasis_line2 = models.CharField(max_length=1, choices=EMPHASIS_CHOICES, default='', blank=True)
    text_size_line2 = models.PositiveIntegerField(default=8)
    text_color_line2 = ColorField(default='#000000')  # ColorField for color picker
    
    font_line3 = models.CharField(max_length=20, choices=FONT_CHOICES, default='helvetica')
    emphasis_line3 = models.CharField(max_length=1, choices=EMPHASIS_CHOICES, default='', blank=True)
    text_size_line3 = models.PositiveIntegerField(default=8)
    text_color_line3 = ColorField(default='#000000')  # ColorField for color picker
    
    font_line4 = models.CharField(max_length=20, choices=FONT_CHOICES, default='helvetica')
    emphasis_line4 = models.CharField(max_length=1, choices=EMPHASIS_CHOICES, default='', blank=True)
    text_size_line4 = models.PositiveIntegerField(default=8)
    text_color_line4 = ColorField(default='#000000')  # ColorField for color picker

    def __str__(self):
        return str(self.user.username)


