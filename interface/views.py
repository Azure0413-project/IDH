from django.shortcuts import render
from django.http import HttpResponse
import json
from datetime import datetime

# Create your views here.

time = datetime(2022, 7, 5, 8, 30, 12)

def index(request):
    return render(request, 'index.html')
