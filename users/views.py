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

from .models import Profile,Subscription,Payment,Contact

from .utils import remove_expired_users_from_group
from .signals import createProfile,createSettings

from .utils import generate_current_datetime, send_verification_email
from datetime import timedelta
from django.utils import timezone

from django.core.exceptions import ObjectDoesNotExist

from .forms import CustomPasswordChangeForm
from django.contrib.auth import update_session_auth_hash


from decouple import config

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode


# Create your views here.
def home(request):
    plans = Subscription.objects.all()
    context = {
        'plans':plans
    }
    return render(request,"home.html",context)


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
            return render(request, "users/login_register.html", context)


        user  =  authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)

            messages.success(request,"User successfully logged in")
            for group in request.user.groups.all():
                if group.name == 'admin':
                    return redirect('profiles')
            return redirect('profile')
        else:
            messages.error(request,"Username or password is incorrect")
            return render(request, "users/login_register.html", context)


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
           phone = form.cleaned_data.get('phone')
           
           createProfile(sender=User, instance=user, created=True, phone=phone) 
           createSettings(sender=User, instance=user, created=True) 
           
           group = Group.objects.get(name='registeredUsers') 
           user.groups.add(group)

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
    extend_subscription_button = False 
    plans = Subscription.objects.all()
    try:
        # return utc payment instance
        latest_payment = Payment.objects.filter(profile__user=user).latest('expiry_date')
        # converting into my timezone
        latest_payment_date = timezone.localtime(latest_payment.expiry_date).replace(tzinfo=None)
          
        # Check if the payment has expired
        if latest_payment_date < generate_current_datetime():
            messages.warning(request,"Please renew your payment as it has already expired.")
        else:
            # Calculate the difference between the payment expiry date and current time
            time_difference = latest_payment_date - generate_current_datetime()
            # Check if the payment is about to expire (within one month)
            days_left = time_difference.days

            if time_difference <= timedelta(days=30):
                if days_left > 1:
                    message = f"Your subscription is going to expire in {days_left} days."
                elif days_left <= 1:
                    message = "Your subscription is going to expire soon."

                extend_subscription_button = True
                messages.warning(request, message)     
  

    except Payment.DoesNotExist:
        messages.info(request,"Please make a payment to use our service")

    groups = Group.objects.filter(user=user)
    group_values = [group.name for group in groups]


    payment_details = Payment.objects.filter(profile__user=user)
    
    context = {
        'groups':group_values,
        'payment_details':payment_details,
        'extend_subscription_button': extend_subscription_button,
        'plans':plans,
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


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and number and subject and message :
            # Save the form data to the Contact model
            contact = Contact(name=name, email=email, number=number, subject=subject, message=message)
            contact.save()
            # Return a success response
            messages.success(request, 'Thank you for reaching to us. Your message will be responded shortly!!')
            return redirect("home")


    return render(request, 'home.html')


@login_required(login_url="login")
@allowed_users(allowed_roles=['registeredUsers'])
def api_request(request,pk):
    user = request.user
    # fetching user profile and subscription plan
    profile = Profile.objects.get(user=user)
    subscription_plan=Subscription.objects.get(id=pk)
    # setting user details and subscription details
    username=profile.username
    email=profile.email 
    subscription_plan_id=subscription_plan.id
    subscription_plan_type=subscription_plan.plan
    subscription_plan_price=float(subscription_plan.price)

    # api call
    url = "https://a.khalti.com/api/v2/epayment/initiate/"
    
    api_key = config('KHALTI_API_KEY')

    headers = {
        "Content-Type":"application/json",
        "Authorization": f"Key {api_key}" 
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
    try:
        if "payment_url" in response:
            payment_url = response['payment_url']
            return HttpResponseRedirect(payment_url)
        elif("error_key" in response):
            return render(request, 'users/error.html', context)	
        else:
            return render(request, 'users/error.html', context)
    except Exception as e:
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
    

    # payment details
    pidx = request.GET['pidx']
    txnId = request.GET['txnId']
    amount = request.GET['amount']
    mobile = request.GET['mobile']
    purchase_order_id = request.GET['purchase_order_id']
    purchase_order_name = request.GET['purchase_order_name']


    subscription_plan=Subscription.objects.get(id=purchase_order_id)
    duration = subscription_plan.get_duration()

    api_key = config('KHALTI_API_KEY')
    # payment verification look up
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    request_data = {
		'pidx':pidx,
	}

    headers = {
            'Content-Type': 'application/json',
            "Authorization": f"Key {api_key}", 
    }

    response = requests.post(url, json=request_data,headers=headers)
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
                    expiry_date=latest_payment.expiry_date + duration,
                    txnId = txnId,
                    status = "active"
                )
            else:
                # The latest payment's expiry_date has expired, set new expiry_date from now
                payment = Payment(
                    profile=profile,
                    subscription=subscription_plan,
                    amount=amount,
                    expiry_date=generate_current_datetime() + duration,
                    txnId = txnId,
                    status = "active"
                )
        except ObjectDoesNotExist:
            # No prior payment exists, set new expiry_date from now
            payment = Payment(
                profile=profile,
                subscription=subscription_plan,
                amount=amount,
                expiry_date=generate_current_datetime() + duration,
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
    form = CustomPasswordChangeForm(request.user)
    if request.method == 'POST':

        form = CustomPasswordChangeForm(request.user, request.POST)

        if(form.is_valid()):
            user = form.save()
            update_session_auth_hash(request, user)  # Update session
            messages.success(request, 'Password was successfully updated!! Please log in again')
            logout(request)  # Log out the user
            return redirect('login')
    
    context = {
        'form':form,
    }
    return render(request,"changePassword.html",context)


#forgot Password Link
def forgot_password(request):
    page = "forgot_password"
    if request.method == 'POST':
        email = request.POST['email']
        
        if Profile.objects.filter(email=email).exists():
            user_profile = Profile.objects.get(email=email)
            user = user_profile.user

            # send reset password email
            mail_subject = 'Reset Your Password'
            email_template = 'users/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
    return render(request, 'users/forgot_password.html',{'page':page})


def reset_password_validate(request, uidb64, token):
    # validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def reset_password(request):
    page = "forgot_password"
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    return render(request, 'users/reset_password.html',{'page':page})    