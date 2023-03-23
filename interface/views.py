from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
import datetime
from datetime import datetime, timedelta
from interface.models import Patient, Dialysis, Record, Feedback
from django.core import serializers
from interface.model.prediction import predict_idh
from scripts.fetch_API import fetchData
from scripts.DBbuilder import splitCSV
from scripts.load_data import saveData

# Create your views here.

time = datetime.now()
# time = datetime(2023, 2, 22, 11, 38, 0)

b_area = ['B5', 'B9', 'B3', 'B8', 'B2', 'B7', 'B1', 'B6']
c_area = ['C5', 'C9', 'C3', 'C8', 'C2', 'C7', 'C1', 'C6']
d_area = ['D5', 'D9', 'D3', 'D8', 'D2', 'D7', 'D1', 'D6']
a_area = ['A9', '', 'A5', '', 'A3', 'A8', 'A2', 'A7', 'A1', 'A6']
e_area = ['', '', 'E5', 'E8', 'E3', 'E7', 'E2', 'E6', 'E1', '']
i_area = ['', '', 'I2', '', 'I1', '']

def index(request, area="dashboard"):
    corn_job()
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

def get_record(request, shift):
    if request.method == 'POST':
        idh_list = request.POST.get('idh-patients-list')
        tmp_form = request.POST.get('idh-tmp-form')
        tmp_list = tmp_form.split('/')
        update_idh = idh_list.split('-')[0:-1]
        # print(request.POST)
        t, shift, patients = get_update_idh_patients(shift, update_idh, tmp_list)
        return render(request, 'feedback.html', {
            "form": False,
            "t": t,
            "shift": shift,
            "a_patients": patients["a_patients"],
            "b_patients": patients["b_patients"],
            "c_patients": patients["c_patients"],
            "d_patients": patients["d_patients"],
            "e_patients": patients["e_patients"],
            "i_patients": patients["i_patients"],
            "idh_patients": patients["idh_patients"],
            "idh_bed": patients["idh_bed"],
        })
    else:
        t, shift, patients = get_idh_patients(shift)
        return render(request, 'feedback.html', {
            "form": True,
            "t": t,
            "shift": shift,
            "a_patients": patients["a_patients"],
            "b_patients": patients["b_patients"],
            "c_patients": patients["c_patients"],
            "d_patients": patients["d_patients"],
            "e_patients": patients["e_patients"],
            "i_patients": patients["i_patients"],
            "idh_patients": patients["idh_patients"],
            "idh_bed": patients["idh_bed"],
        })

def get_patients():
    now_dialysis = Dialysis.objects.filter(start_time__lte=time, end_time__gte=time)
    a_patients = []
    b_patients = []
    c_patients = []
    d_patients = []
    e_patients = []
    i_patients = []
    all_idh = predict_idh()
    flag = 0
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
                patient['idh'] = int(round(all_idh[flag] * 100))
                flag += 1
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
                patient['idh'] = int(round(all_idh[flag] * 100))
                flag += 1
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
                patient['idh'] = int(round(all_idh[flag] * 100))
                flag += 1
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
                patient['idh'] = int(round(all_idh[flag] * 100))
                flag += 1
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
                patient['idh'] = int(round(all_idh[flag] * 100))
                flag += 1
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
                patient['idh'] = int(round(all_idh[flag] * 100))
                flag += 1
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
    all_dialysis = Dialysis.objects.filter(p_id=d.p_id.p_id, times__gte=d.times-2)
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

def get_idh_patients(shift):
    t = shift
    if shift == 0:
        shift = "早"
        shift_start = time.replace(hour=10, minute=0)
        shift_end = time.replace(hour=12, minute=0)
        print(shift_start, shift_end)
    elif shift == 1:
        shift = "午"
        shift_start = time.replace(hour=14, minute=0)
        shift_end = time.replace(hour=16, minute=0)
    else:
        shift = "晚"
        shift_start = time.replace(hour=19, minute=0)
        shift_end = time.replace(hour=21, minute=0)

    now_dialysis = Dialysis.objects.filter(start_time__lte=shift_start, end_time__gte=shift_end)
    # start = Dialysis.objects.filter(start_time__lte=time, end_time__gte=time).earliest("start_time").start_time
    # end = Dialysis.objects.filter(start_time__lte=time, end_time__gte=time).latest("end_time").end_time
    a_patients = []
    b_patients = []
    c_patients = []
    d_patients = []
    e_patients = []
    i_patients = []
    idh_patients = []
    idh_bed = ''
    for index, bed in enumerate(a_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time)
                patient['record'] = records[len(records) - 1]
                patient['status'] = False
                plot_data = []
                for r in records:
                    if r.SBP <= 90 and r.SBP != 0:
                        patient['status'] = True
                        for re in records:
                            timestamp = str(re.record_time.strftime("%Y-%m-%d %H:%M"))
                            sbp = float(re.SBP)
                            pulse = re.pulse
                            cvp = re.CVP
                            plot_data.append({
                                "timestamp": timestamp,
                                "SBP": sbp,
                                "pulse": pulse,
                                "CVP": cvp, 
                            })
                        patient['chart_id'] = "linechart-" + str(bed)
                        patient['chart'] = json.dumps(plot_data)
                        idh_patients.append(patient)
                        idh_bed += bed + '-'
                        break
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
                patient['record'] = records[len(records) - 1]
                patient['status'] = False
                plot_data = []
                for r in records:
                    if r.SBP <= 90 and r.SBP != 0:
                        patient['status'] = True
                        for re in records:
                            timestamp = str(re.record_time.strftime("%Y-%m-%d %H:%M"))
                            sbp = float(re.SBP)
                            pulse = re.pulse
                            cvp = re.CVP
                            plot_data.append({
                                "timestamp": timestamp,
                                "SBP": sbp,
                                "pulse": pulse,
                                "CVP": cvp, 
                            })
                        patient['chart_id'] = "linechart-" + str(bed)
                        patient['chart'] = json.dumps(plot_data)
                        idh_patients.append(patient)
                        idh_bed += bed + '-'
                        break
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
                patient['record'] = records[len(records) - 1]
                patient['status'] = False
                plot_data = []
                for r in records:
                    if r.SBP <= 90 and r.SBP != 0:
                        patient['status'] = True
                        for re in records:
                            timestamp = str(re.record_time.strftime("%Y-%m-%d %H:%M"))
                            sbp = float(re.SBP)
                            pulse = re.pulse
                            cvp = re.CVP
                            plot_data.append({
                                "timestamp": timestamp,
                                "SBP": sbp,
                                "pulse": pulse,
                                "CVP": cvp, 
                            })
                        patient['chart_id'] = "linechart-" + str(bed)
                        patient['chart'] = json.dumps(plot_data)
                        idh_patients.append(patient)
                        idh_bed += bed + '-'
                        break
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
                patient['record'] = records[len(records) - 1]
                patient['status'] = False
                plot_data = []
                for r in records:
                    if r.SBP <= 90 and r.SBP != 0:
                        patient['status'] = True
                        for re in records:
                            timestamp = str(re.record_time.strftime("%Y-%m-%d %H:%M"))
                            sbp = float(re.SBP)
                            pulse = re.pulse
                            cvp = re.CVP
                            plot_data.append({
                                "timestamp": timestamp,
                                "SBP": sbp,
                                "pulse": pulse,
                                "CVP": cvp, 
                            })
                        patient['chart_id'] = "linechart-" + str(bed)
                        patient['chart'] = json.dumps(plot_data)
                        idh_patients.append(patient)
                        idh_bed += bed + '-'
                        break
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
                patient['record'] = records[len(records) - 1]
                patient['status'] = False
                plot_data = []
                for r in records:
                    if r.SBP <= 90 and r.SBP != 0:
                        patient['status'] = True
                        for re in records:
                            timestamp = str(re.record_time.strftime("%Y-%m-%d %H:%M"))
                            sbp = float(re.SBP)
                            pulse = re.pulse
                            cvp = re.CVP
                            plot_data.append({
                                "timestamp": timestamp,
                                "SBP": sbp,
                                "pulse": pulse,
                                "CVP": cvp, 
                            })
                        patient['chart_id'] = "linechart-" + str(bed)
                        patient['chart'] = json.dumps(plot_data)
                        idh_patients.append(patient)
                        idh_bed += bed + '-'
                        break
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        e_patients.append(patient)
    for index, bed in enumerate(i_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time)
                patient['record'] = records[len(records) - 1]
                patient['status'] = False
                plot_data = []
                for r in records:
                    if r.SBP <= 90 and r.SBP != 0:
                        patient['status'] = True
                        for re in records:
                            timestamp = str(re.record_time.strftime("%Y-%m-%d %H:%M"))
                            sbp = float(re.SBP)
                            pulse = re.pulse
                            cvp = re.CVP
                            plot_data.append({
                                "timestamp": timestamp,
                                "SBP": sbp,
                                "pulse": pulse,
                                "CVP": cvp, 
                            })
                        patient['chart_id'] = "linechart-" + str(bed)
                        patient['chart'] = json.dumps(plot_data)
                        idh_patients.append(patient)
                        idh_bed += bed + '-'
                        break
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        i_patients.append(patient)

    return t, shift, {
        'a_patients': a_patients, 
        'b_patients': b_patients, 
        'c_patients': c_patients,
        'd_patients': d_patients,
        'e_patients': e_patients,
        'i_patients': i_patients,
        'idh_patients': idh_patients,
        'idh_bed': idh_bed,
    }

def get_update_idh_patients(shift, update_idh, tmp_list):
    t = shift
    if shift == 0:
        shift = "早"
        shift_start = time.replace(hour=10, minute=0)
        shift_end = time.replace(hour=12, minute=0)
        print(shift_start, shift_end)
    elif shift == 1:
        shift = "午"
        shift_start = time.replace(hour=14, minute=0)
        shift_end = time.replace(hour=16, minute=0)
    else:
        shift = "晚"
        shift_start = time.replace(hour=19, minute=0)
        shift_end = time.replace(hour=21, minute=0)
    now_dialysis = Dialysis.objects.filter(start_time__lte=shift_start, end_time__gte=shift_end)
    # start = Dialysis.objects.filter(start_time__lte=time, end_time__gte=time).earliest("start_time").start_time
    # end = Dialysis.objects.filter(start_time__lte=time, end_time__gte=time).latest("end_time").end_time
    a_patients = []
    b_patients = []
    c_patients = []
    d_patients = []
    e_patients = []
    i_patients = []
    idh_patients = []
    idh_bed = ''
    for index, bed in enumerate(a_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time)
                patient['record'] = records[len(records) - 1]
                patient['status'] = False
                plot_data = []
                if bed in update_idh:
                    patient['status'] = True
                    plot_data = []
                    for re in records:
                        timestamp = str(re.record_time.strftime("%Y-%m-%d %H:%M"))
                        sbp = float(re.SBP)
                        pulse = re.pulse
                        cvp = re.CVP
                        plot_data.append({
                            "timestamp": timestamp,
                            "SBP": sbp,
                            "pulse": pulse,
                            "CVP": cvp, 
                        })
                    patient['chart_id'] = "linechart-" + str(bed)
                    patient['chart'] = json.dumps(plot_data)
                    for p in tmp_list:
                        pid = p.split('-')[0]
                        if pid == str(patient['id'].p_id):
                            info = p.split('-')[1].split('+')
                            sign = info[0]                       
                            if sign == '1': patient['sign'] = True
                            elif sign == '0': patient['sign'] = False
                            if 'drug' in info: patient['drug'] = True
                            if 'inject' in info: patient['inject'] = True
                            if 'setting' in info: patient['set'] = True
                            if 'other' in info: patient['other'] = True
                    idh_patients.append(patient)
                    idh_bed += bed + '-'
                    continue
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
                patient['record'] = records[len(records) - 1]
                patient['status'] = False
                plot_data = []
                if bed in update_idh:
                    patient['status'] = True
                    plot_data = []
                    for re in records:
                        timestamp = str(re.record_time.strftime("%Y-%m-%d %H:%M"))
                        sbp = float(re.SBP)
                        pulse = re.pulse
                        cvp = re.CVP
                        plot_data.append({
                            "timestamp": timestamp,
                            "SBP": sbp,
                            "pulse": pulse,
                            "CVP": cvp, 
                        })
                    patient['chart_id'] = "linechart-" + str(bed)
                    patient['chart'] = json.dumps(plot_data)
                    for p in tmp_list:
                        pid = p.split('-')[0]
                        if pid == str(patient['id'].p_id):
                            info = p.split('-')[1].split('+')
                            sign = info[0]                       
                            if sign == '1': patient['sign'] = True
                            elif sign == '0': patient['sign'] = False
                            if 'drug' in info: patient['drug'] = True
                            if 'inject' in info: patient['inject'] = True
                            if 'setting' in info: patient['set'] = True
                            if 'other' in info: patient['other'] = True
                    idh_patients.append(patient)
                    idh_bed += bed + '-'
                    continue
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
                patient['record'] = records[len(records) - 1]
                patient['status'] = False
                plot_data = []
                if bed in update_idh:
                    patient['status'] = True
                    plot_data = []
                    for re in records:
                        timestamp = str(re.record_time.strftime("%Y-%m-%d %H:%M"))
                        sbp = float(re.SBP)
                        pulse = re.pulse
                        cvp = re.CVP
                        plot_data.append({
                            "timestamp": timestamp,
                            "SBP": sbp,
                            "pulse": pulse,
                            "CVP": cvp, 
                        })
                    patient['chart_id'] = "linechart-" + str(bed)
                    patient['chart'] = json.dumps(plot_data)
                    for p in tmp_list:
                        pid = p.split('-')[0]
                        if pid == str(patient['id'].p_id):
                            info = p.split('-')[1].split('+')
                            sign = info[0]                       
                            if sign == '1': patient['sign'] = True
                            elif sign == '0': patient['sign'] = False
                            if 'drug' in info: patient['drug'] = True
                            if 'inject' in info: patient['inject'] = True
                            if 'setting' in info: patient['set'] = True
                            if 'other' in info: patient['other'] = True
                    idh_patients.append(patient)
                    idh_bed += bed + '-'
                    continue
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
                patient['record'] = records[len(records) - 1]
                patient['status'] = False
                plot_data = []
                if bed in update_idh:
                    patient['status'] = True
                    plot_data = []
                    for re in records:
                        timestamp = str(re.record_time.strftime("%Y-%m-%d %H:%M"))
                        sbp = float(re.SBP)
                        pulse = re.pulse
                        cvp = re.CVP
                        plot_data.append({
                            "timestamp": timestamp,
                            "SBP": sbp,
                            "pulse": pulse,
                            "CVP": cvp, 
                        })
                    patient['chart_id'] = "linechart-" + str(bed)
                    patient['chart'] = json.dumps(plot_data)
                    for p in tmp_list:
                        pid = p.split('-')[0]
                        if pid == str(patient['id'].p_id):
                            info = p.split('-')[1].split('+')
                            sign = info[0]                       
                            if sign == '1': patient['sign'] = True
                            elif sign == '0': patient['sign'] = False
                            if 'drug' in info: patient['drug'] = True
                            if 'inject' in info: patient['inject'] = True
                            if 'setting' in info: patient['set'] = True
                            if 'other' in info: patient['other'] = True
                    idh_patients.append(patient)
                    idh_bed += bed + '-'
                    continue
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
                patient['record'] = records[len(records) - 1]
                patient['status'] = False
                plot_data = []
                if bed in update_idh:
                    patient['status'] = True
                    plot_data = []
                    for re in records:
                        timestamp = str(re.record_time.strftime("%Y-%m-%d %H:%M"))
                        sbp = float(re.SBP)
                        pulse = re.pulse
                        cvp = re.CVP
                        plot_data.append({
                            "timestamp": timestamp,
                            "SBP": sbp,
                            "pulse": pulse,
                            "CVP": cvp, 
                        })
                    patient['chart_id'] = "linechart-" + str(bed)
                    patient['chart'] = json.dumps(plot_data)
                    for p in tmp_list:
                        pid = p.split('-')[0]
                        if pid == str(patient['id'].p_id):
                            info = p.split('-')[1].split('+')
                            sign = info[0]                       
                            if sign == '1': patient['sign'] = True
                            elif sign == '0': patient['sign'] = False
                            if 'drug' in info: patient['drug'] = True
                            if 'inject' in info: patient['inject'] = True
                            if 'setting' in info: patient['set'] = True
                            if 'other' in info: patient['other'] = True
                    idh_patients.append(patient)
                    idh_bed += bed + '-'
                    continue
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        e_patients.append(patient)
    for index, bed in enumerate(i_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time)
                patient['record'] = records[len(records) - 1]
                patient['status'] = False
                plot_data = []
                if bed in update_idh:
                    patient['status'] = True
                    plot_data = []
                    for re in records:
                        timestamp = str(re.record_time.strftime("%Y-%m-%d %H:%M"))
                        sbp = float(re.SBP)
                        pulse = re.pulse
                        cvp = re.CVP
                        plot_data.append({
                            "timestamp": timestamp,
                            "SBP": sbp,
                            "pulse": pulse,
                            "CVP": cvp, 
                        })
                    patient['chart_id'] = "linechart-" + str(bed)
                    patient['chart'] = json.dumps(plot_data)
                    for p in tmp_list:
                        pid = p.split('-')[0]
                        if pid == str(patient['id'].p_id):
                            info = p.split('-')[1].split('+')
                            sign = info[0]                       
                            if sign == '1': patient['sign'] = True
                            elif sign == '0': patient['sign'] = False
                            if 'drug' in info: patient['drug'] = True
                            if 'inject' in info: patient['inject'] = True
                            if 'setting' in info: patient['set'] = True
                            if 'other' in info: patient['other'] = True
                    idh_patients.append(patient)
                    idh_bed += bed + '-'
                    continue
                continue
        if 'id' not in patient:
            patient['id'] = '---'
        i_patients.append(patient)

    return t, shift, {
        'a_patients': a_patients, 
        'b_patients': b_patients, 
        'c_patients': c_patients,
        'd_patients': d_patients,
        'e_patients': e_patients,
        'i_patients': i_patients,
        'idh_patients': idh_patients,
        'idh_bed': idh_bed,
    }

def post_feedback(request):
    if request.method == 'POST':
        sign = []
        treatment = []
        p_id = request.POST.getlist('patient')
        for id in p_id:
            sign.append(request.POST.get('sign-' + id))
            treatment.append(request.POST.getlist('treatment-' + id))
        setting = request.POST.getlist('setting')
        bands = request.POST.getlist("bands")[0].split(',')
        for index, id in enumerate(p_id):
            dialysis = Dialysis.objects.get(d_id=setting[index])
            is_sign = True if sign[index] == '1' else False
            is_drug = True if 'drug' in treatment[index] else False
            is_inject= True if 'inject' in treatment[index] else False
            is_setting = True if 'setting' in treatment[index] else False
            is_other = True if 'other' in treatment[index] else False
            f = Feedback(d_id=dialysis, is_sign=is_sign, is_drug=is_drug, is_inject=is_inject, is_setting=is_setting, is_other=is_other)
            f.save()
        for idh in bands:
            if idh != '':
                patient = idh.split('-')[0]
                record = idh.split('-')[2]
                d = Dialysis.objects.filter(p_id=patient, start_time__lt=time)
                r = Record.objects.filter(d_id=d[d.count()-1])[int(record)]
                f = Record.objects.get(r_id=r.r_id)
                f.is_idh = True
                f.save()
        print("Successfully fill in the feedback form")
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

def corn_job():
    fetchData()
    # print("Successfully fetch API")
    splitCSV()
    # print("Successfully split to 3 CSV files")
    saveData()
    print("Successfully save new data to database")