from django.shortcuts import render
from django.http import HttpResponse
import json
from datetime import datetime
from interface.models import Patient, Dialysis, Record

# Create your views here.

time = datetime(2022, 7, 5, 8, 30, 12)
bed = ['A1', 'A2', 'A3', 'A5', 'A6', 'A7', 'A8', 'A9', 
       'B1', 'B2', 'B3', 'B5', 'B6', 'B7', 'B8', 'B9', 
       'C1', 'C2', 'C3', 'C5', 'C6', 'C7', 'C8', 'C9', 
       'D1', 'D2', 'D3', 'D5', 'D6', 'D7', 'D8', 'D9', 
       'E1', 'E2', 'E3', 'E5', 'E6', 'E7', 'E8', 
       'I1', 'I2']

def index(request):
    patients = get_patient()
    return render(request, 'index.html', {
        "patients": patients,
    })

def get_patient():
    patients = Dialysis.objects.filter(start_time__lte=time, end_time__gte=time)
    return len(patients)