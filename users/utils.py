from django.utils import timezone
from django.contrib.auth.models import Group
from .models import Payment
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.db.models import Max

def remove_expired_users_from_group(user):
    group = Group.objects.get(name="subscribers")
    print("checking for removal")
    try:
        # Retrieve the latest payment for the user
        latest_payment = Payment.objects.filter(profile__user=user).latest('expiry_date')          
        latest_payment_date = timezone.localtime(latest_payment.expiry_date).replace(tzinfo=None)
        print("For ",latest_payment)        
        # Check if the user has a latest payment
        print("Latest expiry date:", latest_payment_date)
        print("current time",generate_current_datetime())

        if latest_payment_date < generate_current_datetime():
            print("expiring user")
            user.groups.remove(group)
            latest_payment.status = 'expired'
        else:
            print("chances of exception")
            user.groups.add(group)
            latest_payment.status = 'active'
            print("no exceptions")

        latest_payment.save()

    except ObjectDoesNotExist:
        # Handle the case where no matching Payment instance is found
        # For example, you can log a message or perform alternative actions
        print("No matching Payment instance found for the user.",user)
        group_values = user.groups.values_list('name', flat=True)
        print(group_values)
        payments = Payment.objects.all()
        for payment in payments:
            expiry_date = timezone.localtime(payment.expiry_date).replace(tzinfo=None)
            if expiry_date < generate_current_datetime():
                payment.status = 'expired'
            else:
                payment.status = 'active'
                
            payment.save()     

        # returning the latest payment for the associated users in the payment table
        # latest_payments = Payment.objects.values('profile__user__username').annotate(expiry_date=Max('expiry_date'))

        # for payment in latest_payments:
        #     print(payment)
        #     user = payment['profile__user__username']
        #     latest_expiry = payment['expiry_date']
        #     latest_expiry = timezone.localtime(latest_expiry).replace(tzinfo=None)
        #     # Do something with the user and latest expiry_date, such as printing or further processing
        #     print(f"User : {user}, Latest Expiry: {latest_expiry}")


            # if latest_expiry < generate_current_datetime():
            #     user.groups.remove(group)
            #     latest_payment.status = 'expired'
            # else:
            #     user.groups.add(group)
            #     latest_payment.status = 'active'

        if 'admin' not in group_values:
            print("here")
            user.groups.remove(group)


def generate_current_datetime():
    current_datetime = datetime.datetime.now()
    return current_datetime