from django.shortcuts import render,redirect
from django.contrib.auth.models import User,Group
from django.contrib.auth import login,authenticate,logout

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm

from .decorators import *
from django.contrib.auth.decorators import login_required

import requests
from django.http import HttpResponseRedirect

from .models import Profile,Subscription,Payment

from .utils import remove_expired_users_from_group
from .signals import createProfile

from .utils import generate_current_datetime
from datetime import timedelta
from django.utils import timezone

from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# Create your views here.
def home(request):
    context = {        
    }
    return render(request,"users/home.html",context)


@unauthenticated_user
def loginUser(request):
    if request.user.is_authenticated:
        # previous_url = request.META.get('HTTP_REFERER')
        # return redirect(previous_url)  
        return redirect('home')
    
    page = "login"
    context = {
        'page':page
    }

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username) 
        except:
            messages.error(request,"Username or password does not exist")
            print("username does not exist")

        user  =  authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)

            messages.success(request,"User successfully logged in")
            return redirect('home')
        else:
            messages.error(request,"Username or password is incorrect")
            print("username or password is incorrect")    

    return render(request,"users/login_register.html",context)


@unauthenticated_user
def registerUser(request):
    if request.user.is_authenticated:
        # previous_url = request.META.get('HTTP_REFERER')
        # return redirect(previous_url)  
        return redirect('home')

    page = "register"
    form = CustomUserCreationForm()  
    

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
           user = form.save(commit=False)
           user.username = user.username.lower() 
           user.save() 
           print("signal calls...") 
           phone = form.cleaned_data.get('phone')
           
           createProfile(sender=User, instance=user, created=True, phone=phone) 

           group = Group.objects.get(name='registeredUsers') 
           user.groups.add(group)

           messages.success(request,"cheers "+user.username+"!!! Your account was successfully created.")

           login(request,user)
           return redirect('profile')  
    
    context = {
        'form':form,
        'page':page,
    }

    return render(request,'users/login_register.html',context)


@login_required(login_url="login")
@allowed_users(allowed_roles=['registeredUsers'])
def profile(request):
    user = request.user
    

    try:
        # return utc payment instance
        latest_payment = Payment.objects.filter(profile__user=user).latest('expiry_date')
        # converting into my timezone
        latest_payment_date = timezone.localtime(latest_payment.expiry_date).replace(tzinfo=None)

        print("profile page")
        print(latest_payment_date)
        print(generate_current_datetime())

        # Check if the payment has expired
        if latest_payment_date < generate_current_datetime():
            messages.warning(request,"Please renew your payment as it has already expired.")
        else:
            # Calculate the difference between the payment expiry date and current time
            time_difference = latest_payment_date - generate_current_datetime()
            days_left = time_difference.days
            # Check if the payment is about to expire (within one month)
            if time_difference <= timedelta(days=30):
                message = f"Your subscription is going to expire in {days_left} days."
                messages.warning(request, message)
            else:
                messages.info(request,"Your subscription is active")

    except Payment.DoesNotExist:
        messages.info(request,"No payment information found. Please make a payment to use of software")

    groups = Group.objects.filter(user=user)
    group_values = [group.name for group in groups]
    context ={
        'groups':group_values
    }
    return render(request,"users/users_page.html",context)


@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def dashboard(request):
    return render(request,"users/admin_page.html")


def logoutUser(request):
    logout(request)
    messages.success(request,"User was successfully logged out")
    return redirect("login")    


@login_required(login_url="login")
@allowed_users(allowed_roles=['registeredUsers'])
def api_request(request):
    print(request.user)
    user = request.user
    # fetching user profile and subscription plan
    profile = Profile.objects.get(user=user)
    subscription_plan=Subscription.objects.get(plan="standard")
    # setting user details and subscription details
    username=profile.username
    email=profile.email 
    subscription_plan_id=subscription_plan.id
    subscription_plan_type=subscription_plan.plan
    subscription_plan_price=float(subscription_plan.price)

    print(subscription_plan_price)
    # api call
    url = "https://a.khalti.com/api/v2/epayment/initiate/"
    
    headers = {
        "Content-Type":"application/json",
        "Authorization": "Key 84a068d414ff4a189e1dbae85a09c9a3" 
    }

    payload = {
        "return_url": "http://127.0.0.1:8000/process_order//",
        "website_url": "http://127.0.0.1:8000/",
        "amount": subscription_plan_price*100,
        "purchase_order_id": subscription_plan_id,
        "purchase_order_name": subscription_plan_type,
        "customer_info": {
            "name": username,
            "email": email,
        },
        "product_details": [
            {
                "identity": subscription_plan_id,
                "name": subscription_plan_type,
                "total_price": subscription_plan_price*100,
                "quantity": 1,
                "unit_price": subscription_plan_price*100
            }
        ]
    }


    response = requests.post(url,json=payload,headers=headers)

    response = response.json()
    context={
        'response':response
    }
    print(response)
    try:
        if "payment_url" in response:
            payment_url = response['payment_url']
            return HttpResponseRedirect(payment_url)
        elif("error_key" in response):
            return render(request, 'users/error.html', context)	
        else:
            return render(request, 'users/error.html', context)
    except Exception as e:
        print("exception")
        # Handle the exception
        exception_type = type(e).__name__  # Get the name of the exception type
        exception_message = str(e)  # Get the error message of the exception
        
        # Handle the exception accordingly, such as displaying an error message
        context = {
            'exception_type': exception_type,
            'exception_message': exception_message
        }
        return HttpResponse("Payment Failed")



@login_required(login_url="login")
@allowed_users(allowed_roles=['registeredUsers'])
def processOrder(request):
    # user details and subscription details
    profile = request.user.profile
    user = request.user
    subscription_plan=Subscription.objects.get(plan="standard")

    # payment details
    pidx = request.GET['pidx']
    txnId = request.GET['txnId']
    amount = request.GET['amount']
    mobile = request.GET['mobile']
    purchase_order_id = request.GET['purchase_order_id']
    purchase_order_name = request.GET['purchase_order_name']

    # payment verification look up
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    request_data = {
		'pidx':pidx,
	}

    headers = {
            'Content-Type': 'application/json',
            "Authorization": "key 84a068d414ff4a189e1dbae85a09c9a3", 
    }

    response = requests.post(url, json=request_data,headers=headers)
    print("here")
    response=response.json()

    # Get the payment status from the response
    payment_status = response.get('status')

    # Define the respective messages for different payment statuses
    messages = {
        'Completed': 'Payment was successful.',
        'Pending': 'Payment is pending. Please wait for confirmation.',
        'Refunded': 'Payment was refunded.',
        'Expired': 'Payment has expired. Please make a new payment.',
    }

    # Get the corresponding message based on the payment status
    payment_message = messages.get(payment_status, 'incorrect Authorization key or incorrect payment ID is passed.')

    context = {
        'response': response,
        'payment_message': payment_message
    }

    print(response['status'])
    if(response['status']=='Completed'):
        group_values = [group.name for group in user.groups.all()]
        amount = subscription_plan.price
        if Payment.objects.filter(txnId=txnId).exists():
            messages.info("Payment with"+txnId+"already exists")
            return redirect("profile")

        try:
            # return utc payment instance
            latest_payment = Payment.objects.filter(profile__user=user).latest('expiry_date')
            # converting into my timezone
            latest_payment_date = timezone.localtime(latest_payment.expiry_date).replace(tzinfo=None)

            # Check if the latest payment's expiry_date has expired
            if latest_payment_date > generate_current_datetime():
                # Update the expiry_date of the new payment
                payment = Payment(
                    profile=profile,
                    subscription=subscription_plan,
                    amount=amount,
                    expiry_date=latest_payment.expiry_date + timedelta(days=366),
                    txnId = txnId,
                    status = "active"
                )
            else:
                # The latest payment's expiry_date has expired, set new expiry_date from now
                payment = Payment(
                    profile=profile,
                    subscription=subscription_plan,
                    amount=amount,
                    expiry_date=generate_current_datetime() + timedelta(days=366),
                    txnId = txnId,
                    status = "active"
                )
        except ObjectDoesNotExist:
            # No prior payment exists, set new expiry_date from now
            payment = Payment(
                profile=profile,
                subscription=subscription_plan,
                amount=amount,
                expiry_date=generate_current_datetime() + timedelta(days=366),
                txnId = txnId,
                status = "active"
            )
            # Add the user to the "subscribers" group
            if 'subscribers' not in group_values:
                group = Group.objects.get(name="subscribers")
                user.groups.add(group)

        payment.save()  

    return render(request,"users/payment_status.html",context)    


@login_required(login_url="login")
def changePassword(request):
    print("password change")
    form = PasswordChangeForm(request.user)
    if request.method == 'POST':

        print("changing password here ")
        form = PasswordChangeForm(request.user, request.POST)

        if(form.is_valid()):
            user = form.save()
            update_session_auth_hash(request, user)  # Update session
            messages.success(request, 'Your password was successfully updated!')
            logout(request)  # Log out the user
            return redirect('login')
    
    context = {
        'form':form
    }
    return render(request,"changePassword.html",context)