from django.urls import path
from . import views

urlpatterns = [
    path('',views.sticker_form,name='sticker_form'),
    path('download/',views.download_pdf,name='download_pdf'),
]