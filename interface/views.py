from django.shortcuts import render
from django.http import HttpResponse
import json
from datetime import datetime
from interface.models import Patient, Dialysis, Record

# Create your views here.

time = datetime(2022, 7, 5, 11, 0, 12)

b_area = ['B5', 'B9', 'B3', 'B8', 'B2', 'B7', 'B1', 'B6']
c_area = ['C5', 'C9', 'C3', 'C8', 'C2', 'C7', 'C1', 'C6']
d_area = ['D5', 'D9', 'D3', 'D8', 'D2', 'D7', 'D1', 'D6']
a_area = ['A9', '', 'A5', '', 'A3', 'A8', 'A2', 'A7', 'A1', 'A6']
e_area = ['', '', 'E5', 'E8', 'E3', 'E7', 'E2', 'E6', 'E1', '']
i_area = ['', '', 'I2', '', 'I1', '']

def index(request):
    patients = get_patients()
    return render(request, 'index.html', {
        "home": True,
        "a_patients": patients["a_patients"],
        "b_patients": patients["b_patients"],
        "c_patients": patients["c_patients"],
        "d_patients": patients["d_patients"],
        "e_patients": patients["e_patients"],
        "i_patients": patients["i_patients"],
    })

def get_patients():
    now_dialysis = Dialysis.objects.filter(start_time__lte=time, end_time__gte=time)
    a_patients = []
    b_patients = []
    c_patients = []
    d_patients = []
    e_patients = []
    i_patients = []
    r_list = []
    for bed in a_area:
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time)
                patient['record'] = r[len(r) - 1]
                r_list.append(patient['record'].r_id)
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        a_patients.append(patient)
    for bed in b_area:
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                # patient['id'] = list(Patient.objects.filter(p_id=d.p_id.p_id).values())
                patient['setting'] = d
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time)
                patient['record'] = r[len(r) - 1]
                r_list.append(patient['record'].r_id)
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        b_patients.append(patient)
    for bed in c_area:
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time)
                patient['record'] = r[len(r) - 1]
                r_list.append(patient['record'].r_id)
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        c_patients.append(patient)
    for bed in d_area:
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d                
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time)
                patient['record'] = r[len(r) - 1]
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        d_patients.append(patient)
    for bed in e_area:
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time)
                patient['record'] = r[len(r) - 1]
                r_list.append(patient['record'].r_id)
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        e_patients.append(patient)
    for bed in i_area:
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if d.bed == bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d    
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time)
                patient['record'] = r[len(r) - 1]
                r_list.append(patient['record'].r_id)
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        i_patients.append(patient)
    # print(r_list)
    return {
        'a_patients': a_patients, 
        'b_patients': b_patients, 
        'c_patients': c_patients,
        'd_patients': d_patients,
        'e_patients': e_patients,
        'i_patients': i_patients,
    }

def get_detail(request, bed):
    patient = {}
    d = Dialysis.objects.filter(bed=bed, start_time__lte=time, end_time__gte=time)[0]
    start_time = d.start_time
    patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
    patient['setting'] = d
    r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time)
    patient['record'] = r[len(r) - 1]
    all_dialysis = Dialysis.objects.filter(p_id=d.p_id.p_id, times__gte=d.times-1)
    print(all_dialysis)
    temp = []
    for dialysis in all_dialysis:
        record_list = Record.objects.filter(d_id=dialysis.d_id, record_time__lte=time)
        for record in record_list:
            temp.append(record) 
    patient['all_record'] = temp
    print(patient['all_record'])
    patients = get_patients()
    return render(request, 'index.html', {
        "home": False,
        "a_patients": patients["a_patients"],
        "b_patients": patients["b_patients"],
        "c_patients": patients["c_patients"],
        "d_patients": patients["d_patients"],
        "e_patients": patients["e_patients"],
        "i_patients": patients["i_patients"],
        "id": patient['id'],
        "setting": patient['setting'],
        "record": patient['record'],
        "all_record": patient['all_record'],
    })