from django.urls import path
from . import views

urlpatterns = [
    path('stickerPrintingSoftware/',views.sticker_form,name='sticker_form'),
    path('labelSettings/',views.labelSettings,name='labelSettings'),
    path('edit_config/',views.edit_config,name='edit_config'),
    path('download/',views.download_pdf,name='download_pdf'),
]