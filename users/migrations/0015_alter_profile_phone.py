# Generated by Django 4.0.3 on 2023-06-07 06:44

from django.db import migrations, models
import users.forms


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_alter_payment_payment_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='phone',
            field=models.CharField(max_length=10, unique=True, validators=[users.forms.validate_ten_digits]),
        ),
    ]
