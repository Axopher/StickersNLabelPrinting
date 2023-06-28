from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('login/',views.loginUser,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('register/',views.registerUser,name='register'),
    path('profile/',views.profile,name='profile'),
    path('api_request/<str:pk>/',views.api_request,name='api_request'),
    path('process_order/',views.processOrder,name='process_order'),
    path('change_password/',views.changePassword,name='change_password'),
    # path('pricing_plan/',views.pricingPlan,name='pricing_plan'),                   

]