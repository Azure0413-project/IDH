from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
import datetime
from datetime import datetime, timedelta
from interface.models import Patient, Dialysis, Record, Feedback, Predict, Warnings, Nurse
from django.core import serializers
from django.db.models import Max
from interface.model.prediction import predict_idh
from scripts.fetch_API import fetchData
from scripts.DBbuilder import splitCSV
from scripts.load_data import saveData
from decimal import Decimal
import numpy as np
from openpyxl import Workbook

# Create your views here.

b_area = ['B5', 'B9', 'B3', 'B8', 'B2', 'B7', 'B1', 'B6']
c_area = ['C5', 'C9', 'C3', 'C8', 'C2', 'C7', 'C1', 'C6']
d_area = ['D5', 'D9', 'D3', 'D8', 'D2', 'D7', 'D1', 'D6']
a_area = ['A9', '', 'A5', '', 'A3', 'A8', 'A2', 'A7', 'A1', 'A6']
e_area = ['', '', 'E5', 'E8', 'E3', 'E7', 'E2', 'E6', 'E1', '']
i_area = ['', '', 'I2', '', 'I1', '']

def get_time():
    now = False #push
    if now:
        time = datetime.now()
    else:
        time = datetime(2023, 9, 23, 10, 43, 0)
    return time

def index(request, area="dashboard"):
    time = get_time()
    if area == "dashboard" and time.minute % 3 == 0: #push要開
        corn_job() 
    if area == 'Z':
        return render(request, 'nurseAreaAdjust.html')
    if area == 'Y':
        if request.method == 'GET':
            nurseList = list(Nurse.objects.all().values())
            print("index Y nurse list:", nurseList)
            return render(request, 'nurseAreaSearch.html', {
                "home": True,
                "patients": [],
                "chart": json.dumps([]),
                'nurseList': nurseList,
            })
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

def NurseAreaSearch(request, nurseId, bedList):
    if bedList != "emp":
        patients = get_nurse_patients(bedList.split("-"))
    else:
        patients = []
    nurseList = list(Nurse.objects.all().values())
    return render(request, 'nurseAreaSearch.html', {
        'nurseList': nurseList,
        "nurseId": nurseId,
        "home": True,
        "patients": patients["nurse_patients"] if len(patients) > 0 else [],
        "chart": json.dumps([]),
    })

def NurseAreaAdjust(request, nurseId):
    if nurseId == "emp":
        nurseId = list(Nurse.objects.all().values())[0]["empNo"]
    nurseList = list(Nurse.objects.all().values())
    return render(request, 'nurseAreaAdjust.html', {
        "nurseId": nurseId,
        'nurseList': nurseList
    })

def NurseList(request):
    if request.method == "GET":
        nurseList = list(Nurse.objects.all().values())
        return render(request, 'nurseAreaNurseList.html', {
            'nurseList': nurseList
        })
    else:
        empNo = request.POST.get("empNo")
        n_name = request.POST.get("nurseName")
        Nurse.objects.create(
            empNo=empNo,
            n_name=n_name
        )
        return JsonResponse({'status': 'success'})
    
def DeleteNurse(request):
    empNo = request.POST.get("empNo")
    Nurse.objects.filter(empNo=empNo).delete()
    return JsonResponse({'status': 'success'})

def get_record(request, shift):
    nurseList = list(Nurse.objects.all().values())
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
            "nurseList": nurseList
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
            "nurseList": nurseList
        })

def get_patients():
    time = get_time()
    now_dialysis = Dialysis.objects.filter(start_time__lte=time, end_time__gte=time)
    a_patients = []
    b_patients = []
    c_patients = []
    d_patients = []
    e_patients = []
    i_patients = []
    if len(now_dialysis) <= 1:
        all_idh = [0]
    else:
        preds = Predict.objects.filter(d_id=now_dialysis[0].d_id).order_by('pred_time').reverse()
        last_pred = datetime.min if len(preds) == 0 else preds[0].pred_time
        # all_idh = predict_idh() #1205
        if datetime.now() >= last_pred + timedelta(hours=1): # 先用 datetime.now() 代替 time
            do_pred = True
            all_idh = predict_idh() #1205
        else:
            do_pred = False
            same_preds = Predict.objects.filter(pred_time__date=preds[0].pred_time.date(), pred_time__hour=preds[0].pred_time.hour).order_by('flag')
            all_pred_idh = [s.pred_idh for s in same_preds]
            all_idh = [np.float32(a) for a in all_pred_idh]
    flag = 0
    for index, bed in enumerate(a_area):
        patient = {}
        patient = {'bed': bed}
        for d in now_dialysis:
            if bed == d.bed:
                start_time = d.start_time
                patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                patient['setting'] = d
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time).order_by('record_time')
                if len(r) == 0:
                    patient['id'] = '---'
                    continue
                else:
                    patient['record'] = r[len(r) - 1]
                patient['idh'] = int(round(all_idh[flag] * 100))

                # print('BED:', bed)
                #1226 warning Feedback 
                w = Warnings.objects.filter(p_bed=bed).order_by('dismiss_time').reverse()
                if len(w) == 0:
                    patient['done_warning'] = True 
                else:
                    # print(w[0].dismiss_time,'---', datetime.now() - timedelta(hours=1))
                    patient['done_warning'] = True if w[0].dismiss_time < datetime.now() - timedelta(hours=1) else False

                #1218改
                if do_pred:
                    dialysis = Dialysis.objects.get(d_id=d.d_id)
                    pred = Predict(d_id=dialysis, flag=flag, pred_idh=Decimal(str(all_idh[flag])))
                    pred.save()
                if flag == 32:
                    continue
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
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time).order_by('record_time')
                if len(r) == 0:
                    patient['id'] = '---'
                    continue
                else:
                    patient['record'] = r[len(r) - 1]
                patient['idh'] = int(round(all_idh[flag] * 100))

                # print('BED:', bed)
                #1226 warning Feedback 
                w = Warnings.objects.filter(p_bed=bed).order_by('dismiss_time').reverse()
                if len(w) == 0:
                    patient['done_warning'] = True 
                else:
                    # print(w[0].dismiss_time,'---', datetime.now() - timedelta(hours=1))
                    patient['done_warning'] = True if w[0].dismiss_time < datetime.now() - timedelta(hours=1) else False

                #1212改
                if do_pred:
                    dialysis = Dialysis.objects.get(d_id=d.d_id)
                    pred = Predict(d_id=dialysis, flag=flag, pred_idh=Decimal(str(all_idh[flag])))
                    pred.save()
                if flag == 32:
                    continue
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
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time).order_by('record_time')
                if len(r) == 0:
                    patient['id'] = '---'
                    continue
                else:
                    patient['record'] = r[len(r) - 1]
                patient['idh'] = int(round(all_idh[flag] * 100))

                # print('BED:', bed)
                #1226 warning Feedback 
                w = Warnings.objects.filter(p_bed=bed).order_by('dismiss_time').reverse()
                if len(w) == 0:
                    patient['done_warning'] = True 
                else:
                    # print(w[0].dismiss_time,'---', datetime.now() - timedelta(hours=1))
                    patient['done_warning'] = True if w[0].dismiss_time < datetime.now() - timedelta(hours=1) else False

                #1212改
                if do_pred:
                    dialysis = Dialysis.objects.get(d_id=d.d_id)
                    pred = Predict(d_id=dialysis, flag=flag, pred_idh=Decimal(str(all_idh[flag])))
                    pred.save()
                if flag == 32:
                    continue
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
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time).order_by('record_time')
                if len(r) == 0:
                    patient['id'] = '---'
                    continue
                else:
                    patient['record'] = r[len(r) - 1]
                patient['idh'] = int(round(all_idh[flag] * 100))

                # print('BED:', bed)
                #1226 warning Feedback 
                w = Warnings.objects.filter(p_bed=bed).order_by('dismiss_time').reverse()
                if len(w) == 0:
                    patient['done_warning'] = True 
                else:
                    # print(w[0].dismiss_time,'---', datetime.now() - timedelta(hours=1))
                    patient['done_warning'] = True if w[0].dismiss_time < datetime.now() - timedelta(hours=1) else False

                #1212改
                if do_pred:
                    dialysis = Dialysis.objects.get(d_id=d.d_id)
                    pred = Predict(d_id=dialysis, flag=flag, pred_idh=Decimal(str(all_idh[flag])))
                    pred.save()
                if flag == 32:
                    continue
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
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time).order_by('record_time')
                if len(r) == 0:
                    patient['id'] = '---'
                    continue
                else:
                    patient['record'] = r[len(r) - 1]
                patient['idh'] = int(round(all_idh[flag] * 100))

                # print('BED:', bed)
                #1226 warning Feedback 
                w = Warnings.objects.filter(p_bed=bed).order_by('dismiss_time').reverse()
                if len(w) == 0:
                    patient['done_warning'] = True 
                else:
                    # print(w[0].dismiss_time,'---', datetime.now() - timedelta(hours=1))
                    patient['done_warning'] = True if w[0].dismiss_time < datetime.now() - timedelta(hours=1) else False

                #1212改
                if do_pred:
                    dialysis = Dialysis.objects.get(d_id=d.d_id)
                    pred = Predict(d_id=dialysis, flag=flag, pred_idh=Decimal(str(all_idh[flag])))
                    pred.save()
                if flag == 32:
                    continue
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
                r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time).order_by('record_time')
                if len(r) == 0:
                    patient['id'] = '---'
                    continue
                else:
                    patient['record'] = r[len(r) - 1]
                patient['idh'] = int(round(all_idh[flag] * 100))

                # print('BED:', bed)
                #1226 warning Feedback 
                w = Warnings.objects.filter(p_bed=bed).order_by('dismiss_time').reverse()
                if len(w) == 0:
                    patient['done_warning'] = True 
                else:
                    # print(w[0].dismiss_time,'---', datetime.now() - timedelta(hours=1))
                    patient['done_warning'] = True if w[0].dismiss_time < datetime.now() - timedelta(hours=1) else False

                #1212改
                if do_pred:
                    dialysis = Dialysis.objects.get(d_id=d.d_id)
                    pred = Predict(d_id=dialysis, flag=flag, pred_idh=Decimal(str(all_idh[flag])))
                    pred.save()
                if flag == 32:
                    continue
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
    time = get_time()
    patient = {}
    d = Dialysis.objects.filter(bed=bed, start_time__lte=time, end_time__gte=time)[0]
    start_time = d.start_time
    # patient data
    patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
    # latest dialysis information
    patient['setting'] = d
    # latest dialysis record
    r_today = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time).order_by('record_time')
    patient['record'] = r_today[len(r_today) - 1]

    # all record
    all_dialysis = Dialysis.objects.filter(p_id=d.p_id.p_id, times__gte=d.times-2)
    temp = []
    for dialysis in all_dialysis:
        record_list = Record.objects.filter(d_id=dialysis.d_id, record_time__lte=time).select_related().order_by('record_time')
        for record in record_list:
            if record.d_id.temperature <= 0: record.d_id.temperature = '-'
            if record.d_id.start_temperature <= 0: record.d_id.start_temperature = '-'
            if record.d_id.ESA == str(-1): record.d_id.ESA = '-'
            if record.flush == -1.000: record.flush = '-'
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

    # plot 
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
    time =get_time()
    t = shift
    if shift == 0:
        shift = "早"
        shift_start = time.replace(hour=10, minute=0)
        shift_end = time.replace(hour=11, minute=0)
    elif shift == 1:
        shift = "午"
        shift_start = time.replace(hour=15, minute=0)
        shift_end = time.replace(hour=16, minute=0)
    else:
        shift = "晚"
        shift_start = time.replace(hour=20, minute=0)
        shift_end = time.replace(hour=21, minute=0)

    now_dialysis = Dialysis.objects.filter(start_time__lte=shift_start, end_time__gte=shift_end)
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
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time).order_by('record_time')
                if len(records) == 0:
                    continue
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
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time).order_by('record_time')
                if len(records) == 0:
                    continue
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
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time).order_by('record_time')
                if len(records) == 0:
                    continue
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
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time).order_by('record_time')
                if len(records) == 0:
                    continue
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
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time).order_by('record_time')
                if len(records) == 0:
                    continue
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
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time).order_by('record_time')
                if len(records) == 0:
                    continue
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
    time = get_time()
    t = shift
    if shift == 0:
        shift = "早"
        shift_start = time.replace(hour=10, minute=0)
        shift_end = time.replace(hour=12, minute=0)
    elif shift == 1:
        shift = "午"
        shift_start = time.replace(hour=14, minute=0)
        shift_end = time.replace(hour=16, minute=0)
    else:
        shift = "晚"
        shift_start = time.replace(hour=19, minute=0)
        shift_end = time.replace(hour=21, minute=0)
    now_dialysis = Dialysis.objects.filter(start_time__lte=shift_start, end_time__gte=shift_end)
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
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time).order_by('record_time')
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
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time).order_by('record_time')
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
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time).order_by('record_time')
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
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time).order_by('record_time')
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
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time).order_by('record_time')
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
                records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time).order_by('record_time')
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
    time = get_time()
    if request.method == 'POST':
        sign = []
        treatment = []
        idh_time = []
        p_id = request.POST.getlist('patient')
        for id in p_id:
            sign.append(request.POST.get('sign-' + id))
            treatment.append(request.POST.getlist('treatment-' + id))
            idh_time.append(request.POST.getlist('idh-time-' + id)) #0110
        setting = request.POST.getlist('setting')
        if len(request.POST.getlist("bands")) > 0:
            bands = request.POST.getlist("bands")[0].split(',')
            for index, id in enumerate(p_id):
                dialysis = Dialysis.objects.get(d_id=setting[index])
                is_sign = True if sign[index] == '1' else False
                is_drug = True if 'drug' in treatment[index] else False
                is_inject= True if 'inject' in treatment[index] else False
                is_setting = True if 'setting' in treatment[index] else False
                is_other = True if 'other' in treatment[index] else False
                f = Feedback(d_id=dialysis, is_sign=is_sign, is_drug=is_drug, is_inject=is_inject, is_setting=is_setting, is_other=is_other, idh_time=idh_time[index]) 
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

def warning_feedback(request):
    # 1210改
    if request.method == 'POST':
        time = datetime.now()
        dismiss_time = time
        empNo = request.POST.get('empNo')
        warning_SBP = request.POST.get('SBP')
        warning_DBP = request.POST.get('DBP')
        pBed = request.POST.get('patientBed')
        pName = request.POST.get('patientName')
        print(f'{time} \nempNo: {empNo}, SBP: {warning_SBP}, DBP: {warning_DBP}, \npatientBed: {pBed}, patientName: {pName}')
        try:
            w = Warnings(dismiss_time=dismiss_time, empNo=empNo, p_bed=pBed, p_name=pName, warning_SBP=warning_SBP, warning_DBP=warning_DBP)
            w.save()
            return JsonResponse({"status": 'success'})
        except Exception as error:
            return JsonResponse({"status": 'fail', "msg": str(error)})

def get_nurse_patients(bed_list):
    # if request.method == 'POST':
    #   bed_list = request.POST.getlist('nurse_bed') 
    # bed_list = ["A1", "A2", "A5", "B2", "B7"]
    patients = get_patients()
    nurse_patients = []
    for index, bed in enumerate(bed_list):
        for p_area in patients.keys():
            for p in patients[p_area]:
                if p['bed'] == bed:
                    nurse_patients.append(p)
    return {'nurse_patients': nurse_patients}

def get_nurse_detail(request, nurseId, bed, idh):
    time = get_time()
    patient = {}
    d = Dialysis.objects.filter(bed=bed, start_time__lte=time, end_time__gte=time)[0]
    start_time = d.start_time
    # patient data
    patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
    # latest dialysis information
    patient['setting'] = d
    # latest dialysis record
    r_today = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time).order_by('record_time')
    patient['record'] = r_today[len(r_today) - 1]

    # all record
    all_dialysis = Dialysis.objects.filter(p_id=d.p_id.p_id, times__gte=d.times-2)
    temp = []
    for dialysis in all_dialysis:
        record_list = Record.objects.filter(d_id=dialysis.d_id, record_time__lte=time).select_related().order_by('record_time')
        for record in record_list:
            if record.d_id.temperature <= 0: record.d_id.temperature = '-'
            if record.d_id.start_temperature <= 0: record.d_id.start_temperature = '-'
            if record.d_id.ESA == str(-1): record.d_id.ESA = '-'
            if record.flush == -1.000: record.flush = '-'
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
    patients = get_nurse_patients([bed])
    
    # plot 
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

    return render(request, 'nurseAreaSearch.html', {
        "nurseId": nurseId,
        "home": False,
        "nurse_patients": patients["nurse_patients"], #1226
        "id": patient['id'],
        "setting": patient['setting'],
        "record": patient['record'],
        "idh": idh,
        "diff": diff,
        "all_record": patient['all_record'],
        "chart": json.dumps(plot_data),
    })

def export_file():
    '''0109 Export patient data to Excel file'''
    # Create the export view 
    filename = f'PatientData_{datetime.now().strftime("%Y%m%d")}.xlsx'
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    wb = Workbook()
    ws = wb.active
    ws.title = "all_record"
    ws.append(["工號", "姓名", "床位", "SBP", "DBP"])
    warnings = Warnings.objects.all()
    if len(warnings) != 0:
        for warning in warnings:
            ws.append([warning.empNo, warning.p_name, warning.p_name, warning.warning_SBP, warning.warning_DBP])
    # Save the workbook to the HttpResponse
    wb.save(response)
    return response

def corn_job():
    fetchData()
    # print("Successfully fetch API")
    splitCSV()
    # print("Successfully split to 3 CSV files")
    saveData()
    print("Successfully save new data to database")