from django.utils import timezone
from django.contrib.auth.models import Group
from .models import Payment
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.db.models import Max


from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, message
from django.conf import settings
from django.core.mail import EmailMessage
from .models import Profile

def remove_expired_users_from_group(user):
    group = Group.objects.get(name="subscribers")
    try:
        # Retrieve the latest payment for the user
        latest_payment = Payment.objects.filter(profile__user=user).latest('expiry_date')          
        latest_payment_date = timezone.localtime(latest_payment.expiry_date).replace(tzinfo=None)

        if latest_payment_date < generate_current_datetime():
            user.groups.remove(group)
            latest_payment.status = 'expired'
        else:
            user.groups.add(group)
            latest_payment.status = 'active'

        latest_payment.save()

    except ObjectDoesNotExist:
        # Handle the case where no matching Payment instance is found
        # For example, you can log a message or perform alternative actions
        group_values = user.groups.values_list('name', flat=True)
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
            user.groups.remove(group)


def generate_current_datetime():
    current_datetime = datetime.datetime.now()
    return current_datetime


def send_verification_email(request, user, mail_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    user_profile = Profile.objects.get(user=user)
    message = render_to_string(email_template, {
        'user': user_profile,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    to_email = user_profile.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.content_subtype = "html"
    mail.send()    