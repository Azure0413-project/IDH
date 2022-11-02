from django.shortcuts import render
from django.http import HttpResponse
import json

# Create your views here.

def index(request):
    with open('interface/data/data.json', encoding="utf-8") as file:
        data = json.loads(file.read())
    return render(request, 'index.html')
