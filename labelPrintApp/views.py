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

# Create your views here.
def sticker_form(request): 
    context = {
        'label_data':label_data,
        'options' : keys
    }    
     
    if request.method == 'POST':
        uploaded_file = request.FILES.get('csv')       
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

            # Create a PDF object
            pdf = FPDF(orientation='P', unit='mm', format='A4')
        

            # Fetch margins data and font related from config file                     
            print(label_info)
            left_right_margin = label_info['left_right_margin']
            top_bottom_margin = label_info['top_bottom_margin']
            font_family = label_info['font']
            style = label_info['emphasis']
            text_size = label_info['text-size']                   

            # Set the margins
            pdf.set_margins(left=left_right_margin, right=left_right_margin, top=top_bottom_margin)

            # Set auto page break with the specified margin
            pdf.set_auto_page_break(auto=True, margin=top_bottom_margin)

            # Set the font style and size
            pdf.set_font(font_family,style,text_size)

            # Add a page
            pdf.add_page()


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
                            pdf.cell(cell_width, cell_height, '', border=1)

                            if(datum.startswith("http")):
                                print("img")
                                # Fetch the image from the web
                                image_url = ""+datum+""
                                image_data = urllib.request.urlopen(image_url).read()
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
                            pdf.cell(cell_width, cell_height, '', border=1)
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


def download_pdf(request):
    # Create a download link for the PDF file
    pdf_directory = "pdf_files"
    pdf_filename = "labels.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_directory, pdf_filename)

    # Generate the response
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="labels.pdf"'
    return response