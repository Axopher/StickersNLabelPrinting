from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import Profile
from labelPrintApp.models import LabelConfig
from .forms import CustomUserCreationForm



def createProfile(sender,instance,created, phone=None,**kwargs):
    if created:
        print("inside signals")
        print(phone)
        user = instance
        profile = Profile.objects.create(
            user=user,
            username=user.username,
            email=user.email,
            phone=phone,
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






    


