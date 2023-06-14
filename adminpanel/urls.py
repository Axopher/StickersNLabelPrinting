from django.urls import path
from . import views

urlpatterns = [
    path('profiles/',views.profiles,name='profiles'),
    path('registeredUsers/',views.registeredUsers,name='registered_users'),
    path('profile/<str:username>/',views.profile,name="profile"),
    path('create_payment/',views.createPayment,name="create_payment"),
    path('update_payment/<str:pk>/',views.updatePayment,name="update_payment"),            
    # path('delete_payment/<str:pk>/',views.deletePayment,name="delete_payment"),
    path('confirm_payment/',views.confirmPayment,name="confirm_payment"),             
]