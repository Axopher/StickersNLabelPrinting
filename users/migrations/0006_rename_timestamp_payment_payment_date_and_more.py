# Generated by Django 4.0.3 on 2023-05-30 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_payment_subscription_plan'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='timestamp',
            new_name='payment_date',
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='subscription_plan',
            new_name='subscription',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='active',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='expiry',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='user',
        ),
        migrations.AddField(
            model_name='payment',
            name='expiry_date',
            field=models.DateTimeField(default='2023-06-15 18:30:00'),
        ),
    ]