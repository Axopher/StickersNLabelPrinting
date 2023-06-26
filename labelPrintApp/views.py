from django.shortcuts import render, redirect
from django.http import HttpResponse,FileResponse

from django.contrib import messages


from django.conf import settings
import os


from django.contrib.auth.decorators import login_required
from users.decorators import *

from .forms import LabelConfigForm
from .models import LabelConfig


from .oddyConfig import label_data,keys

from .pdf_generator import process_uploaded_file

# Create your views here.

@login_required(login_url="login")
def edit_config(request):
    user = request.user
    label_config = LabelConfig.objects.get(user=user) 
    form = LabelConfigForm(instance=label_config)
    
    if request.method == 'POST':
        form = LabelConfigForm(request.POST,instance=label_config)
        if form.is_valid():
            form.user = user
            form.save()
            messages.success(request,"settings saved")
            return redirect('edit_config')

    context = {'form':form}
    return render(request,"labelPrintApp/edit_settings.html",context)


@login_required(login_url="login")
@allowed_users(['admin', 'subscribers'])
def sticker_form(request):
    if request.method == 'POST':
        return process_sticker_form(request)
    else:
        return render_sticker_form(request)


def process_sticker_form(request):
    uploaded_file = request.FILES.get('csv')
    if uploaded_file:
        return process_uploaded_file(request, uploaded_file)
    else:
        return render_sticker_form(request)        


def render_sticker_form(request):
    context = {
        'label_data': label_data,
        'options': keys
    }
    return render(request, 'labelPrintApp/form.html', context=context)


@login_required(login_url="login")
@allowed_users(['admin','subscribers'])
def download_pdf(request):
    # Create a download link for the PDF file
    pdf_directory = "pdf_files"
    pdf_filename = "labels.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_directory, pdf_filename)

    # Generate the response
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="labels.pdf"'
    return response