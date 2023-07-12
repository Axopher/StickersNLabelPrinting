from django.db import models
from django.contrib.auth.models import User
import uuid


from datetime import timedelta
from django.db import models
from django.utils import timezone

from django.core.exceptions import ValidationError
from .forms import validate_ten_digits


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    username = models.CharField(max_length=200,blank=True,null=True)
    email = models.EmailField(max_length=500,blank=True,null=True,unique=True)
    phone = models.CharField(max_length=10,unique=True,validators=[validate_ten_digits])
    # profile_image = models.ImageField(null=True,blank=True,upload_to="",default="")
    id = models.UUIDField(default=uuid.uuid4,unique=True,primary_key=True,editable=False)
    created = models.DateTimeField(auto_now_add=True)
    # is_subscribed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.username)


class Subscription(models.Model):
    PLAN_CHOICES = [
        ('Quarterly', 'Quarterly'),
        ('Annually', 'Annually'),
    ]

    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    name = models.CharField(max_length=20,null=True,blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return str(self.plan)

    def get_duration(self):
        if self.plan == 'Quarterly':
            return timedelta(days=91)
        elif self.plan == 'Annual':
            return timedelta(days=366)

class Payment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(blank=True,null=True)
    status = models.CharField(max_length=10, choices=(('active', 'Active'), ('expired', 'Expired')), default='active')
    txnId = models.CharField(max_length=100, blank=True, null=True, unique=True)


    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return str(self.profile)

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    number = models.CharField(max_length=20)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name   

# def save(self, *args, **kwargs):
#         if not self.payment_date:
#             self.payment_date = timezone.now()

#         # executes when the payment instance is new and has not yet been saved to the database.
#         if not self.pk:
#             # Check if the user has a previous payment instance
#             if self.profile.payment_set.exists():
#                 # Get the latest previous payment instance
#                 previous_payment = self.profile.payment_set.latest('payment_date')

#                 # Check if the previous payment's expiry date has not passed
#                 if previous_payment.expiry_date >= timezone.now():
#                     # Update expiry_date based on the previous payment's expiry_date
#                     self.expiry_date = previous_payment.expiry_date + timedelta(days=365)
#             else:
#                 # No previous payment instance, set expiry_date as payment_date + one year
#                 self.expiry_date = self.payment_date + timedelta(days=365)

#         # when payment amount is not provided
#         if not self.amount:
#             self.amount = self.subscription.price    

#         # Set the status based on the expiry date
#         if self.expiry_date and self.expiry_date < timezone.now():
#             print("expired")
#             self.status = 'expired'
#         else:
#             self.status = 'active'

#         super().save(*args, **kwargs)

#         # Update status for all payments whose expiry_date has passed
#         self.profile.payment_set.filter(expiry_date__lt=timezone.now()).update(status='expired')

#         # Update user's group membership based on expiry date
#         remove_expired_users_from_group(self.profile.user)    