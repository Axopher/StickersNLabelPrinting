from django.shortcuts import render, redirect
from django.http import HttpResponse,FileResponse
from django.conf import settings
from django.contrib import messages

import urllib.request

from fpdf import FPDF
import qrcode
import os
from .oddyConfig import label_data,keys
import math 
import csv

from django.contrib.auth.decorators import login_required
from users.decorators import *

from .forms import LabelConfigForm
from .models import LabelConfig
from .utils import hex_to_rgb

import sys

# Create your views here.


@login_required(login_url="login")
def labelSettings(request):
    setting_data = LabelConfig.objects.get(user=request.user)
    context = {
        'setting_data':setting_data
    }

    return render(request,"labelPrintApp/settings.html",context)



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
            return redirect('labelSettings')

    context = {'form':form}
    return render(request,"labelPrintApp/edit_settings.html",context)

@login_required(login_url="login")
@allowed_users(['admin','subscribers'])
def sticker_form(request): 
    context = {
        'label_data':label_data,
        'options' : keys
    }    

    if request.method == 'POST':
        uploaded_file = request.FILES.get('csv')  
        print(uploaded_file)     
        # for entire cell
        entire_sheet_dropdown = request.POST.get('entire-sheet-dropdown')       
        # for a specific cell
        selectedLabel = request.POST.get('selectedLabel')
        rows_dropdown = request.POST.get('rows-dropdown')
        columns_dropdown = request.POST.get('columns-dropdown')

        if(entire_sheet_dropdown):
            entire_sheet_dropdown = int(entire_sheet_dropdown) 
            # initialization of dictionary
            label_info = label_data[entire_sheet_dropdown]
            # fetching text color values
        else:
            selectedLabel = int(selectedLabel)
            row_num = int(rows_dropdown)
            column_num = int(columns_dropdown)
            # initialization of dictionary
            label_info = label_data[selectedLabel]

        if uploaded_file:
            print("uploaded file section")

            # Process the CSV file data
            decoded_file = uploaded_file.read().decode('utf-8').splitlines()
            csvreader = csv.reader(decoded_file)
            data = list(csvreader)
            del data[0]
            data = data
            
            label_settings = LabelConfig.objects.get(user=request.user)

            # Create a PDF object
            pdf = FPDF(orientation='P', unit='mm', format='A4')
        
            

            # Fetch margins data and font related from config file                     
            left_right_margin = label_info['left_right_margin']
            top_bottom_margin = label_info['top_bottom_margin']
                          


            # Set the margins
            pdf.set_margins(left=left_right_margin, right=left_right_margin, top=top_bottom_margin)

            # Set auto page break with the specified margin
            pdf.set_auto_page_break(auto=True, margin=top_bottom_margin)

            # Add a page
            pdf.add_page()


            # getting text color values
        
            r,g,b = hex_to_rgb(label_settings.text_color_line1)
            pdf.set_text_color(r,g,b)
            # get the font family,emphasis and size
            font_family = label_settings.font_line1
            style = label_settings.emphasis_line1
            text_size = label_settings.text_size_line1    
            # Set the font style and size
            pdf.set_font(font_family,style,text_size)

            print("first phases")
            # Initializing label data
            cell_width = label_info['cell_width']
            cell_height = label_info['cell_height']
            rows = label_info['rows']
            columns = label_info['columns']
            ver_cell_gap = label_info['ver_cell_gap']
            hor_cell_gap = label_info['hor_cell_gap']

            

            in_cx = (.03027245207*cell_width)
            in_cy = (0.07374631268*cell_height)
            qr_img_area = (0.2678978059*(cell_width*cell_height))
            qr_img_height = math.sqrt(qr_img_area)
            qr_img_width = math.sqrt(qr_img_area)

            if(entire_sheet_dropdown):
                print("for the entire cells")
                
                if(len(data)==entire_sheet_dropdown):
                    # Printing cells both rows and columns-wise
                    for row in range(rows):
                        for col in range(columns):
                            data_list=data[row * columns + col]
                            datum=data_list.pop()
                            print(datum)
                            # Outer cell frame maker
                            pdf.cell(cell_width, cell_height, '', border=0)

                            if(datum.startswith("http")):
                                print("img")
                                # Fetch the image from the web
                                image_url = ""+datum+""
                                try:
                                    image_data = urllib.request.urlopen(image_url).read()
                                except Exception as e:
                                    print(e)
                                    messages.error(request,"Invalid image url")
                                    return redirect("sticker_form")
                                qr_img_path = 'img{}.png'.format(row * columns + col)  # Unique file path
                                with open(qr_img_path, 'wb') as f:
                                    f.write(image_data)
                            else:
                                print("qr")
                                # Generate QR code
                                qr = qrcode.QRCode()
                                qr.add_data(datum)
                                qr.make(fit=True)
                                qr_img = qr.make_image(fill_color="black", back_color="white")

                                # Save QR code image to a temporary file
                                qr_img_path = 'img{}.png'.format(row * columns + col)  # Unique file path
                                qr_img.save(qr_img_path)

                            # Printing qr image file inside cell
                            pdf.image(qr_img_path, x=pdf.get_x()-cell_width+in_cx, y=pdf.get_y()+in_cy, h=qr_img_height, w=qr_img_width)

                            # Remove the temporary QR code image file
                            if os.path.exists(qr_img_path):
                                os.remove(qr_img_path)
                            

                            # adjustment of coordinates
                            reset_x = pdf.get_x()
                            reset_y = pdf.get_y()

                            for i, datum in enumerate(data_list):
                                if i == 0:
                                    pdf.set_xy(pdf.get_x()-(.6059031282*cell_width), pdf.get_y()+in_cy+(1.4*in_cy))

                                
                                # getting settings values for each line
                                text_color = getattr(label_settings, "text_color_line" + str(i + 1))
                                font_type = getattr(label_settings, "font_line" + str(i + 1))
                                style = getattr(label_settings, "emphasis_line" + str(i + 1))
                                text_size = getattr(label_settings, "text_size_line" + str(i + 1))

                                print("printing text color")
                                print(text_color) 

                                r,g,b = hex_to_rgb(text_color)

                                pdf.set_text_color(r,g,b)

                                # Set the font style and size
                                pdf.set_font(font_type,style,text_size)

                                pdf.cell((.5854490414*cell_width), (.1710914454*cell_height), datum, border=0, align="L")
                                pdf.set_xy(pdf.get_x()-(.5854490414*cell_width), pdf.get_y()+(.1710914454*cell_height))

                                if i >= len(data_list)-1:
                                    pdf.set_xy(reset_x, reset_y)

                            if col < columns-1:
                                # Horizontal gap between cells
                                pdf.cell(hor_cell_gap, cell_height, "", border=0)
                            else:
                                # Initializing coordinates for next row
                                pdf.set_xy(left_right_margin, pdf.get_y()+cell_height)

                        if row < rows-1:
                            # Vertical gap between cells
                            pdf.cell(cell_width, ver_cell_gap, "", border=0)
                            pdf.set_xy(pdf.get_x()-cell_width, pdf.get_y()+ver_cell_gap)
                        else:
                            pdf.set_xy(pdf.get_x()-cell_width,pdf.get_y()+ver_cell_gap)

                    # Save the PDF file
                    pdf_filename = 'labels.pdf'
                    pdf_directory = 'pdf_files'
                    pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_directory, pdf_filename)
                    pdf.output(pdf_path)

                    # Check if the file exists
                    if os.path.exists(pdf_path):
                        print("PDF file was created successfully.")
                        return render(request,'labelPrintApp/result.html',{'message':'success'})
                    else:
                        print("Failed to create the PDF file.")
                        return render(request,'labelPrintApp/result.html',{'message':'failed'})
                else:
                    return render(request,'labelPrintApp/result.html',{'message':'Excluding title row, CSV file no. of rows and no. of cells you want to print did not match'})     

            elif(rows_dropdown and columns_dropdown):            
                print("for a specific cell")
                
                if(len(data)==1):                     
                    data_list = data[0]
                    datum=data_list[4]
                    del data_list[4]
                    # Printing cells both rows and columns-wise
                    for row in range(rows):
                        for col in range(columns):                           
                            # Outer cell frame maker
                            pdf.cell(cell_width, cell_height, '', border=0)
                            if(((row+1)==row_num) and ((col+1)==column_num)):
                                if(datum.startswith("http")):
                                    # Fetch the image from the web
                                    image_url = ""+datum+""
                                    image_data = urllib.request.urlopen(image_url).read()
                                    with open('img.png', 'wb') as f:
                                        f.write(image_data)
                                    qr_img_path = 'img.png'
                                else:
                                    # Generate QR code
                                    print("qr")
                                    qr = qrcode.QRCode()
                                    qr.add_data(datum)
                                    qr.make(fit=True)
                                    qr_img = qr.make_image(fill_color="black", back_color="white")

                                    # Save QR code image to a temporary file
                                    qr_img_path = f'img_{row}_{col}.png'
                                    qr_img.save(qr_img_path)

                                # Printing qr image file inside cell
                                pdf.image(qr_img_path, x=pdf.get_x()-cell_width+in_cx, y=pdf.get_y()+in_cy, h=qr_img_height, w=qr_img_width)

                                # Remove the temporary QR code image file
                                if os.path.exists(qr_img_path):
                                    os.remove(qr_img_path)

                                # adjustment of coordinates
                                reset_x = pdf.get_x()
                                reset_y = pdf.get_y()

                                for i, datum in enumerate(data_list):
                                    if i == 0:
                                        pdf.set_xy(pdf.get_x()-(.6059031282*cell_width), pdf.get_y()+in_cy+(1.4*in_cy))

                                    # getting settings values for each line
                                    text_color = getattr(label_settings, "text_color_line" + str(i + 1))
                                    font_type = getattr(label_settings, "font_line" + str(i + 1))
                                    style = getattr(label_settings, "emphasis_line" + str(i + 1))
                                    text_size = getattr(label_settings, "text_size_line" + str(i + 1))

                                    print("printing text color")
                                    print(text_color) 

                                    r,g,b = hex_to_rgb(text_color)

                                    pdf.set_text_color(r,g,b)

                                    # Set the font style and size
                                    pdf.set_font(font_type,style,text_size)


                                    pdf.cell((.5854490414*cell_width), (.1710914454*cell_height), datum, border=0, align="L")
                                    pdf.set_xy(pdf.get_x()-(.5854490414*cell_width), pdf.get_y()+(.1710914454*cell_height))

                                    if i >= len(data_list)-1:
                                        pdf.set_xy(reset_x, reset_y)

                            if col < columns-1:
                                # Horizontal gap between cells
                                pdf.cell(hor_cell_gap, cell_height, "", border=0)
                            else:
                                # Initializing coordinates for next row
                                pdf.set_xy(left_right_margin, pdf.get_y()+cell_height)

                        if row < rows-1:
                            # Vertical gap between cells
                            pdf.cell(cell_width, ver_cell_gap, "", border=0)
                            pdf.set_xy(pdf.get_x()-cell_width, pdf.get_y()+ver_cell_gap)
                        else:
                            pdf.set_xy(pdf.get_x()-cell_width,pdf.get_y()+ver_cell_gap)

                    

                    # Save the PDF file
                    pdf_filename = 'labels.pdf'
                    pdf_directory = 'pdf_files'
                    pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_directory, pdf_filename)
                    pdf.output(pdf_path)

                    # Check if the file exists
                    if os.path.exists(pdf_path):
                        print("PDF file was created successfully.")
                        return render(request,'labelPrintApp/result.html',{'message':'success'})
                    else:
                        print("Failed to create the PDF file.")
                        return render(request,'labelPrintApp/result.html',{'message':'failed'})
                else:
                    print("There should be only one row excluding title row")    
                    return render(request,'labelPrintApp/result.html',{'message':'There should be only one row excluding title row'})            

    return render(request, 'labelPrintApp/form.html',context=context)

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