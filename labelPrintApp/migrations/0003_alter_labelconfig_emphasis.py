# Generated by Django 4.0.3 on 2023-06-15 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labelPrintApp', '0002_alter_labelconfig_text_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labelconfig',
            name='emphasis',
            field=models.CharField(blank=True, choices=[('', 'Regular'), ('B', 'Bold'), ('I', 'Italic'), ('U', 'Underline')], default='', max_length=1),
        ),
    ]
