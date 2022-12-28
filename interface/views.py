from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
import datetime
from datetime import datetime, timedelta
from interface.models import Patient, Dialysis, Record, Feedback
import decimal

# Create your views here.

time = datetime(2022, 7, 5, 10, 50, 12)

b_area = ['B5', 'B9', 'B3', 'B8', 'B2', 'B7', 'B1', 'B6']
c_area = ['C5', 'C9', 'C3', 'C8', 'C2', 'C7', 'C1', 'C6']
d_area = ['D5', 'D9', 'D3', 'D8', 'D2', 'D7', 'D1', 'D6']
a_area = ['A9', '', 'A5', '', 'A3', 'A8', 'A2', 'A7', 'A1', 'A6']
e_area = ['', '', 'E5', 'E8', 'E3', 'E7', 'E2', 'E6', 'E1', '']
i_area = ['', '', 'I2', '', 'I1', '']

a_idh = [0.8030, 0.0000, 0.8489, 0.0000, 0.7675, 0.0158, 0.2934, 0.9592, 0.0489, 0.0581]
b_idh = [0.3267, 0.0176, 0.0318, 0.0698, 0.0581, 0.0367, 0.0075, 0.7248]
c_idh = [0.0098, 0.0928, 0.1114, 0.9328, 0.7162, 0.0194, 0.1287, 0.2848]
d_idh = [0.0098, 0.0000, 0.0245, 0.0000, 0.0191, 0.0000, 0.9229, 0.0000]
e_idh = [0.0000, 0.0000, 0.9863, 0.0073, 0.0242, 0.0125, 0.0000, 0.2468, 0.3468, 0.0000]
i_idh = [0.0000, 0.0000, 0.3927, 0.0000, 0.8806, 0.0000]

def index(request, area="dashboard"):
    patients = get_patients()
    return render(request, 'index.html', {
        "home": True,
        "area": area,
        "a_patients": patients["a_patients"],
        "b_patients": patients["b_patients"],
        "c_patients": patients["c_patients"],
        "d_patients": patients["d_patients"],
        "e_patients": patients["e_patients"],
        "i_patients": patients["i_patients"],
    })

def get_record(request):
    patients = get_idh_patients()
    return render(request, 'feedback.html', {
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
    for index, bed in enumerate(a_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time)
                patient['record'] = r[len(r) - 1]
                patient['idh'] = round(a_idh[index] * 100)
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        a_patients.append(patient)    
    for index, bed in enumerate(b_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time)
                patient['record'] = r[len(r) - 1]
                patient['idh'] = round(b_idh[index] * 100)
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        b_patients.append(patient)
    for index, bed in enumerate(c_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time)
                patient['record'] = r[len(r) - 1]
                patient['idh'] = round(c_idh[index] * 100)
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        c_patients.append(patient)    
    for index, bed in enumerate(d_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d                
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time)
                patient['record'] = r[len(r) - 1]
                patient['idh'] = round(d_idh[index] * 100)
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        d_patients.append(patient)
    for index, bed in enumerate(e_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time)
                patient['record'] = r[len(r) - 1]
                patient['idh'] = round(e_idh[index] * 100)
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        e_patients.append(patient)
    for index, bed in enumerate(i_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if d.bed == bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d    
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time)
                patient['record'] = r[len(r) - 1]
                patient['idh'] = round(i_idh[index] * 100)
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

def get_detail(request, area, bed, idh):
    patient = {}
    d = Dialysis.objects.filter(bed=bed, start_time__lte=time, end_time__gte=time)[0]
    start_time = d.start_time
    # patient data
    patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
    # latest dialysis information
    patient['setting'] = d
    # latest dialysis record
    r_today = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time)
    patient['record'] = r_today[len(r_today) - 1]

    # all record
    all_dialysis = Dialysis.objects.filter(p_id=d.p_id.p_id, times__gte=d.times-1)
    temp = []
    for dialysis in all_dialysis:
        record_list = Record.objects.filter(d_id=dialysis.d_id, record_time__lte=time).select_related()
        for record in record_list:
            if record.d_id.temperature <= 0: record.d_id.temperature = '-'
            if record.d_id.start_temperature <= 0: record.d_id.start_temperature = '-'
            if record.d_id.ESA == str(-1): record.d_id.ESA = '-'
            if record.flush == -1: record.flush = '-'
            temp.append(record)

    patient['all_record'] = temp
    diff = {}
    # weight
    if d.ideal_weight > 0:
        diff_weight = round(d.before_weight - d.ideal_weight, 1)
        diff_percentage = round(diff_weight / d.ideal_weight * 100, 1)
        if diff_weight > 0:
            diff['value'] = '+' + str(diff_weight)
            diff['percentage'] = '+' + str(diff_percentage) + "%"
            diff['per_width'] = diff_percentage * 10
            diff['class'] = 'diff-pos'
        else:
            diff['value'] = str(diff_weight)
            diff['percentage'] = str(diff_percentage) + "%"
            diff['per_width'] = (-1) * diff_percentage * 10
            diff['class'] = 'diff-neg'
    patients = get_patients()
    
    plot_data = []
    for r in r_today:
        timestamp = str(r.record_time.strftime("%Y-%m-%d %H:%M"))
        sbp = float(r.SBP)
        pulse = r.pulse
        cvp = r.CVP
        plot_data.append({
            "timestamp": timestamp,
            "SBP": sbp,
            "pulse": pulse,
            "CVP": cvp, 
        })
    time_string = timestamp
    for i in range(8):
        # if plot_data[i]['SBP'] == 0:
        #     plot_data[i]['SBP'] = None
        # if plot_data[i]['pulse'] == 0:
        #     plot_data[i]['pulse'] = None
        # if plot_data[i]['CVP'] == 0:
        #     plot_data[i]['CVP'] = None
        timestamp = datetime.strptime(time_string, "%Y-%m-%d %H:%M") + timedelta(hours=1)
        time_string = str(timestamp.strftime("%Y-%m-%d %H:%M"))
        if timestamp < d.start_time + timedelta(hours=4):
            if len(plot_data) < 8:
                plot_data.append({
                    "timestamp": time_string,
                    "SBP": None,
                    "pulse": None,
                    "CVP": None,
                })
        else:
            break

    return render(request, 'index.html', {
        "home": False,
        "area": area,
        "a_patients": patients["a_patients"],
        "b_patients": patients["b_patients"],
        "c_patients": patients["c_patients"],
        "d_patients": patients["d_patients"],
        "e_patients": patients["e_patients"],
        "i_patients": patients["i_patients"],
        "id": patient['id'],
        "setting": patient['setting'],
        "record": patient['record'],
        "idh": idh,
        "diff": diff,
        "all_record": patient['all_record'],
        "chart": json.dumps(plot_data),
    })

def get_idh_patients():
    now_dialysis = Dialysis.objects.filter(start_time__lte=time, end_time__gte=time)
    # start = Dialysis.objects.filter(start_time__lte=time, end_time__gte=time).earliest("start_time").start_time
    # end = Dialysis.objects.filter(start_time__lte=time, end_time__gte=time).latest("end_time").end_time
    a_patients = []
    b_patients = []
    c_patients = []
    d_patients = []
    e_patients = []
    i_patients = []
    for index, bed in enumerate(a_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time)
                patient['status'] = False
                for r in records:
                    if r.SBP <= 90 and r.SBP != 0:
                        patient['status'] = True
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        a_patients.append(patient)    
    for index, bed in enumerate(b_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time)
                patient['status'] = False
                for r in records:
                    if r.SBP <= 90 and r.SBP != 0:
                        patient['status'] = True
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        b_patients.append(patient)
    for index, bed in enumerate(c_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time)
                patient['status'] = False
                for r in records:
                    if r.SBP <= 90 and r.SBP != 0:
                        patient['status'] = True
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        c_patients.append(patient)    
    for index, bed in enumerate(d_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d                
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time)
                patient['status'] = False
                for r in records:
                    if r.SBP <= 90 and r.SBP != 0:
                        patient['status'] = True
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        d_patients.append(patient)
    for index, bed in enumerate(e_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time)
                patient['status'] = False
                for r in records:
                    if r.SBP <= 90 and r.SBP != 0:
                        patient['status'] = True
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        e_patients.append(patient)
    for index, bed in enumerate(i_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if d.bed == bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d    
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time)
                patient['status'] = False
                for r in records:
                    if r.SBP <= 90 and r.SBP != 0:
                        patient['status'] = True
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

def get_detail_idh(request):
    if request.method == 'POST':
        beds = request.POST.getlist('idh-patient')
        patients = []
        for bed in beds:
            patient = {}
            d = Dialysis.objects.filter(bed=bed, start_time__lte=time, end_time__gte=time)[0]
            start_time = d.start_time
            # patient data
            patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
            # latest dialysis information
            patient['setting'] = d
            # latest dialysis record
            r_today = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time)
            patient['record'] = r_today[len(r_today) - 1]
            
            plot_data = []
            for r in r_today:
                timestamp = str(r.record_time.strftime("%Y-%m-%d %H:%M"))
                sbp = float(r.SBP)
                pulse = r.pulse
                cvp = r.CVP
                plot_data.append({
                    "timestamp": timestamp,
                    "SBP": sbp,
                    "pulse": pulse,
                    "CVP": cvp, 
                })
            time_string = timestamp
            for i in range(8):
                # if plot_data[i]['SBP'] == 0:
                #     plot_data[i]['SBP'] = None
                # if plot_data[i]['pulse'] == 0:
                #     plot_data[i]['pulse'] = None
                # if plot_data[i]['CVP'] == 0:
                #     plot_data[i]['CVP'] = None
                timestamp = datetime.strptime(time_string, "%Y-%m-%d %H:%M") + timedelta(hours=1)
                time_string = str(timestamp.strftime("%Y-%m-%d %H:%M"))
                if timestamp < d.start_time + timedelta(hours=4):
                    if len(plot_data) < 8:
                        plot_data.append({
                            "timestamp": time_string,
                            "SBP": None,
                            "pulse": None,
                            "CVP": None,
                        })
                else:
                    break
            patient['chart_id'] = "linechart-" + str(bed)
            patient['chart'] = json.dumps(plot_data)
            patients.append(patient)
    all_patients = get_idh_patients()
    return render(request, 'feedback.html', {
        "home": False,
        "patients": patients,
        'b_patients': all_patients['b_patients'], 
        'a_patients': all_patients['a_patients'], 
        'c_patients': all_patients['c_patients'],
        'd_patients': all_patients['d_patients'],
        'e_patients': all_patients['e_patients'],
        'i_patients': all_patients['i_patients'],
    })

def post_feedback(request):
    if request.method == 'POST':
        sign = []
        treatment = []
        p_id = request.POST.getlist('patient')
        for id in p_id:
            sign.append(request.POST.get('sign-' + id))
            treatment.append(request.POST.getlist('treatment-' + id))
        print(p_id)
        print(sign)
        print(treatment)
        patients = get_patients()
        return redirect('/index/dashboard', {
            "home": True,
            "area": 'dashboard',
            "a_patients": patients["a_patients"],
            "b_patients": patients["b_patients"],
            "c_patients": patients["c_patients"],
            "d_patients": patients["d_patients"],
            "e_patients": patients["e_patients"],
            "i_patients": patients["i_patients"],
        })