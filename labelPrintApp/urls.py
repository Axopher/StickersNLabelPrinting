from django.urls import path
from . import views

urlpatterns = [
    path('stickerPrintingSoftware/',views.sticker_form,name='sticker_form'),
    path('download/',views.download_pdf,name='download_pdf'),
]