from django.shortcuts import render
from .models import Medicine
from django.db import DatabaseError
from .serializers import MedicineSerializer
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.http import Http404
from rest_framework.request import Request
import pytesseract
from PIL import Image
import cv2
from .imageHandler import *
from .medicinecheck import *
from .fdadata import get_fda_drug_labels

def landingPage(request):
    return render(request, 'index.html')

def aboutPage(request):
    return render(request, 'about.html')

@api_view(['GET'])
def allMedicine(request):
    try:
        everyMedicine = Medicine.objects.raw("SELECT * FROM mrs_medicine")
        meds = MedicineSerializer(everyMedicine, many=True)
        return Response(meds.data)
    except DatabaseError:
        return Response("No medicine found!", status=404)
    

@api_view(['GET'])
def theMedicine(request, genericName):
    try:
        item = Medicine.objects.get(generic_name=genericName)
        med = MedicineSerializer(item, many=True)
        return Response(med.data)
    except Medicine.DoesNotExist:
        return Response("Medicine not found!", status=404)

@csrf_exempt
@api_view(['POST'])
def imageProcessor(request):
    if request.method == 'POST':
        photo = request.FILES.get('image')
        if not photo:
            return Response('Error 406. Image not received', status=406)
        else:
            try:
                img = Image.open(photo)

                #preprocessing steps starts
                
                #inverted_image = cv2.bitwise_not(img)
                #cv2.imwrite("temp/inverted.jpg", inverted_image)
                
                gray_image = grayscale(img)
                cv2.imwrite("temp/gray.jpg", gray_image)
                thresh, im_bw = cv2.threshold(gray_image, 210, 230, cv2.THRESH_BINARY)
                cv2.imwrite("temp/bw_image.jpg", im_bw)
                 
                no_noise = noise_removal(im_bw)
                cv2.imwrite("temp/no_noise.jpg",no_noise)
                
                eroded_image = thin_font(no_noise)
                cv2.imwrite("temp/eroded_image.jpg", eroded_image)

                dilated_image = thick_font(no_noise)
                cv2.imwrite("temp/dilated_image.jpg", dilated_image)
                
                fixed = deskew(no_noise, dilated_image)
                cv2.imwrite("temp/rotated_fixed.jpg", fixed)

                #preprocessing steps ends

                extractedText = pytesseract.image_to_string(dilated_image)
                if check_medicine_in_database(extractedText):
                    request_object = Request(request)
                    request_object.data['genericName'] = extractedText 
                    response = theMedicine(request_object, genericName=request_object.data['genericName'])
                    return response
                else:
                    openfda_api_key = 'ud5k0qUnvMFw696G2mDwzdsERPUbaVSKM48GIfbQ' #SWETA'S api key
                    result = get_fda_drug_labels(openfda_api_key, extractedText)
                    return Response(result)
            except Exception:
                return Response('Error 500. Cannot extract text from the image.', status=500)    
    else:
        return Response('Error 400. Request method is not POST', status=400)
