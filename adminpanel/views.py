from django.shortcuts import render,redirect
from users.decorators import allowed_users
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User,Group

from django.contrib import messages

from users.models import Payment,Profile,Subscription
from .forms import PaymentForm
from .filters import PaymentFilter, ProfileFilter

from .utils import paginateProfiles
from django.http import HttpResponse

from users.utils import remove_expired_users_from_group
import uuid
from django.core.exceptions import ObjectDoesNotExist

from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from users.utils import generate_current_datetime

from django.db.models import OuterRef, Subquery
# Create your views here.


@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def registeredUsers(request):
    profiles = Profile.objects.all()

    profileFilter = ProfileFilter(request.GET, queryset=profiles)
    profiles = profileFilter.qs.annotate(
        latest_payment_status=Subquery(
            Payment.objects.filter(profile=OuterRef('pk')).order_by('-expiry_date').values('status')[:1]
        )
    )

    custom_range, profiles = paginateProfiles(request, profiles, 10)

    context = {
        'profiles': profiles,
        'profileFilter': profileFilter,
        'custom_range':custom_range
    }


    return render(request,"adminpanel/registeredUsers.html",context)

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def profiles(request):
    payments = Payment.objects.all()


    paymentFilter = PaymentFilter(request.GET,queryset=payments)
    payments = paymentFilter.qs

    # Retrieve the profile IDs for the filtered payments
    profile_ids = payments.values_list('profile_id', flat=True)

    # Filter the profiles based on the retrieved profile IDs
    profiles = Profile.objects.filter(id__in=profile_ids)


    custom_range, payments = paginateProfiles(request, payments, 10)

    context = {
        'payments': payments,
        'paymentFilter': paymentFilter,
        'profiles': profiles , # Add the filtered profiles to the context
        'custom_range':custom_range
    }


    return render(request,"adminpanel/profiles_payment.html",context)

def profile(request,username):
    user = User.objects.get(username=username)
    payments = Payment.objects.filter(profile__user=user)
    
    context = {
        'payments':payments
    }
    return render(request,"adminpanel/single_profile_payment.html",context)

def createPayment(request):
    form = PaymentForm()
    if request.method == "POST":
        form = PaymentForm(request.POST)

        expiry_date = request.POST.get('expiry_date')
        # Convert expiry_date to a datetime object
        expiry_datetime = datetime.strptime(expiry_date, "%Y-%m-%dT%H:%M")

        # Format the expiry_datetime as a readable string
        formatted_expiry_date = expiry_datetime.strftime("%B %d, %Y %I:%M %p")

        phone = request.POST['profile_phone']
        subscription_id = request.POST['subscription']
        subscription_type = Subscription.objects.get(id=subscription_id) 
        try:
            profile = Profile.objects.get(phone=phone)
            if profile and form.is_valid():
                form_data = {
                    'subscription': request.POST.get('subscription'),
                    'amount': request.POST.get('amount'),
                    'expiry_date': request.POST.get('expiry_date'),
                    'status': request.POST.get('status'),
                    'profile_phone': request.POST.get('profile_phone'),
                    'TxnId':"manual_transaction"+str(uuid.uuid4())
                }
                request.session['payment_form_data'] = form_data  # Store form data in the session       
                                     
                return render(request,"adminpanel/paymentConfirmation.html",{'form':form_data,'profile':profile,'subscription_type':subscription_type,'formatted_expiry_date':formatted_expiry_date})                
        except Profile.DoesNotExist:
            print("profile does not exist")
            messages.error(request, 'User must be registered first using this phone number.')

    context = {'form':form}
    return render(request,"adminpanel/payment_form.html",context)



def confirmPayment(request):
    if request.method == "POST":
        # Retrieve the form data from the session
        form_data = request.session.get('payment_form_data')

        subscription_id = form_data['subscription']
        amount = form_data['amount']
        expiry_date = form_data['expiry_date']
        status = form_data['status']
        phone = form_data['profile_phone']
        TxnId = form_data['TxnId']
        print("inside confirm payment")
        print(TxnId)
        expiry_datetime = datetime.strptime(expiry_date, '%Y-%m-%dT%H:%M')
        print(expiry_datetime)
        try:
            # Get the profile and subscription
            print("profile")
            profile = Profile.objects.get(phone=phone)
            print(profile)
            
            latest_payment = Payment.objects.filter(profile=profile).order_by('-expiry_date').first()
            print("latest payment",latest_payment)
            
            
            if not latest_payment:
                # User doesn't have a previous payment or the previous payment has expired
                new_expiry_date = expiry_datetime
                status = "active" 
            else:
                latest_payment_date = timezone.localtime(latest_payment.expiry_date).replace(tzinfo=None)
                if latest_payment_date > generate_current_datetime():
                    print("when payment exists and has not expired")
                    

                    if expiry_datetime < latest_payment_date:
                        messages.error(request,"The expiry date provided by the user is less than the user's latest expiration date")
                        return redirect("create_payment")     
                    else:
                        new_expiry_date = expiry_datetime
                        status = "active" 
                else:
                    new_expiry_date = expiry_datetime
                    status = "active"       


            subscription = Subscription.objects.get(id=subscription_id) 
            # Create a new Payment instance and assign the form data
            payment = Payment()
            payment.subscription = subscription
            payment.amount = amount
            payment.expiry_date = new_expiry_date
            payment.status = status
            payment.profile = profile
            payment.TxnId = TxnId

            # Save the payment
            payment.save()

            # group_values = [group.name for group in profile.user.groups.all()]
            # if 'subscribers' not in group_values:
            #     group = Group.objects.get(name="subscribers")
            #     profile.user.groups.add(group)

            # Clear the payment_form_data from the session
            del request.session['payment_form_data']
            print("payment session deleted")
            print(payment)
            messages.success(request,"Payment created successfully.")
            return redirect("profiles")

        except ObjectDoesNotExist:
            messages.error(request,"Payment creation failed. Invalid profile or subscription.")
            return redirect("create_payment")

    else:
        messages.error(request,"Payment creation failed. Invalid profile or subscription.")
        return redirect("create_payment")


def updatePayment(request,pk):
    payment = Payment.objects.get(id=pk)
    phone = payment.profile.phone
    form = PaymentForm(instance=payment)
    print("Update payment")
    payment.expiry_date = timezone.localtime(payment.expiry_date).replace(tzinfo=None)
    if request.method == "POST":
        print("inside this")
        form = PaymentForm(request.POST,instance=payment)
        if form.is_valid():
            profile = Profile.objects.get(phone=phone)
            profile.phone = phone
            profile.save()
            form.save()

            # Update user's group membership based on expiry date
            remove_expired_users_from_group(payment.profile.user)
            return redirect("profiles")
    
    context = {'form':form,'phone':phone}
    
    return render(request,"adminpanel/payment_form.html",context)

# def deletePayment(request,pk):
#     payment = Payment.objects.get(id=pk)
#     print(payment)
#     if request.method == "POST":
#         payment.delete()
#         return redirect("profiles")
#     context = {'object':payment}
#     return render(request,"adminpanel/delete_template.html",context)    