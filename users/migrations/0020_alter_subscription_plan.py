# Generated by Django 4.0.3 on 2023-06-23 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_alter_payment_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='plan',
            field=models.CharField(choices=[('standard', 'standard')], max_length=10),
        ),
    ]
