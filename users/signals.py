from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import Profile
from labelPrintApp.models import LabelConfig
from .forms import CustomUserCreationForm

from django.core.mail import send_mail
from django.conf import settings

def createProfile(sender,instance,created, phone=None,**kwargs):
    if created:
        user = instance
        profile = Profile.objects.create(
            user=user,
            username=user.username,
            email=user.email,
            phone=phone,
        )

        subject = 'Welcome to LabelPro!!!'
        message = 'We are glad you are here.'

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [profile.email], #multiple emails can passed here
            fail_silently = False
        )



def createSettings(sender,instance,created, phone=None,**kwargs):
    if created:
        user = instance
        LabelConfig.objects.create(
            user=user
        )



def deleteUser(sender,instance,**kwargs):
    # print("delete signal triggered")
    user = instance.user
    user.delete() 

# post_save.connect(createProfile,sender=User)
post_delete.connect(deleteUser,sender=Profile)






    


