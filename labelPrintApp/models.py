from django.db import models

# Create your models here.

class StickerForm(models.Model):
    label_type = models.CharField(max_length=50)
    per_sheet_dropdown = models.IntegerField()
    rows_dropdown = models.IntegerField(blank=True, null=True)
    columns_dropdown = models.IntegerField(blank=True, null=True)
    csv = models.FileField(upload_to='csv_files/')
