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

now = False
def get_time():
    now = False
    # now = True #push要改True
    if now:
        time = datetime.now()
    else:
        # time = datetime(2024, 4, 19, 9, 2, 0)
        time = datetime(2023, 9, 23, 10, 43, 0)
    print(time)
    return time

def index(request, area="dashboard"):
    time = get_time()
    # if area == "dashboard" and time.minute % 3 == 0: #push要開
    #     corn_job() 
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
    # Do corn job at start
    patients = get_patients()
    
    if all(all(i['id'] == '---' for i in p) for p in list(patients.values())):
        print("Success corn job at start")
        # corn_job() 
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

# 護理師專區
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

# 取得資料
def get_record(request, shift):
    nurseList = list(Nurse.objects.all().values())
    if request.method == 'POST':
        idh_list = request.POST.get('idh-patients-list')
        update_idh = idh_list.split('-')[0:-1]
        t, shift, patients = get_update_idh_patients(shift, update_idh)
        form = False
        print("update_idh:", update_idh)
        print("idh_bed:", patients["idh_bed"])
    else:
        t, shift, patients = get_idh_patients(shift)
        form = True
    return render(request, 'feedback.html', {
        "form": form,
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
        do_pred = False
    else:
        preds = Predict.objects.filter(d_id=now_dialysis[0].d_id).order_by('pred_time').reverse()
        last_pred = datetime.min if len(preds) == 0 else preds[0].pred_time
        if datetime.now() >= last_pred + timedelta(minutes=5): # 先用 datetime.now() 代替 time
            do_pred = True
            all_idh = predict_idh() #1205
            print("[prediction]", time)
        else:
            do_pred = False
            same_preds = Predict.objects.filter(pred_time__date=preds[0].pred_time.date(), pred_time__hour=preds[0].pred_time.hour).order_by('flag')
            all_pred_idh = [s.pred_idh for s in same_preds]
            all_idh = [np.float32(a) for a in all_pred_idh]
    flag = 0
    all_area = [a_area, b_area, c_area, d_area, e_area, i_area]
    all_patients = [a_patients, b_patients, c_patients, d_patients, e_patients, i_patients]
    for a in range(len(all_area)):
        for index, bed in enumerate(all_area[a]):
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
                    try:
                        patient['idh'] = int(round(all_idh[flag] * 100))
                    except:
                        patient['idh'] = 0
                    #0326 random code
                    patient['random_code'] = d.random_code
                    #0326 first click 
                    w = Warnings.objects.filter(p_bed=bed).order_by('click_time').reverse()
                    if len(w) == 0:
                        patient['first_click'] = False 
                    else:
                        patient['first_click'] = False if w[0].click_time < datetime.now() - timedelta(hours=1) else True
                    #1226 warning Feedback 
                    w = Warnings.objects.filter(p_bed=bed).order_by('dismiss_time').reverse()
                    if len(w) == 0 or w[0].dismiss_time == None:
                        patient['done_warning'] = False 
                    else:
                        patient['done_warning'] = False if w[0].dismiss_time < datetime.now() - timedelta(hours=1) else True
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
            all_patients[a].append(patient)
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
            if record.record_time > (datetime.now() - timedelta(minutes=10)): record.in10minutes = True
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
    a_patients, b_patients, c_patients, d_patients, e_patients, i_patients = [], [], [], [], [], []
    idh_patients = []
    idh_bed = ''
    all_area = [a_area, b_area, c_area, d_area, e_area, i_area]
    all_patients = [a_patients, b_patients, c_patients, d_patients, e_patients, i_patients]
    for a in range(len(all_area)):
        for index, bed in enumerate(all_area[a]):
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
                    patient['status'] = 0
                    plot_data = []
                    for r in range(len(records)):
                        if records[r].SBP <= 90 and records[r].SBP != 0:
                            patient['status'] = 1
                            for r in range(len(records)):
                                if r > 1 and records[r].SBP < records[r-1].SBP - 20 and records[r].SBP != 0:
                                    patient['status'] = 3
                                    break
                        elif r > 1 and records[r].SBP < records[r-1].SBP - 20 and records[r].SBP != 0:
                            patient['status'] = 2
                    if patient['status'] != 0:
                        idh_patients.append(patient)
                        idh_bed += bed + '-'
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
            if 'id' not in patient:
                patient['id'] = '---' 
            all_patients[a].append(patient)
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

def get_update_idh_patients(shift, update_idh):
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
    a_patients, b_patients, c_patients, d_patients, e_patients, i_patients = [], [], [], [], [], []
    idh_patients = []
    idh_bed = ''
    all_area = [a_area, b_area, c_area, d_area, e_area, i_area]
    all_patients = [a_patients, b_patients, c_patients, d_patients, e_patients, i_patients]
    for a in range(len(all_area)):
        for index, bed in enumerate(all_area[a]):
            patient = {}
            patient = {'bed': bed}
            for d in now_dialysis:
                if bed == d.bed:
                    start_time = d.start_time
                    patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                    patient['setting'] = d
                    records = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=d.end_time).order_by('record_time')
                    patient['record'] = records[len(records) - 1]
                    patient['status'] = 0
                    plot_data = []
                    for r in range(len(records)):
                        if records[r].SBP <= 90 and records[r].SBP != 0:
                            patient['status'] = 1
                            if bed not in idh_bed: idh_bed += bed + '-'
                            for r in range(len(records)):
                                if r > 1 and records[r].SBP < records[r-1].SBP - 20 and records[r].SBP != 0:
                                    patient['status'] = 3
                                    if bed not in idh_bed: idh_bed += bed + '-'
                                    break
                        elif r > 1 and records[r].SBP < records[r-1].SBP - 20 and records[r].SBP != 0:
                            patient['status'] = 2
                            if bed not in idh_bed: idh_bed += bed + '-'
                    if bed in update_idh:
                        idh_patients.append(patient)
                        
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
            if 'id' not in patient:
                patient['id'] = '---'
            all_patients[a].append(patient)  
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

# 回饋表單
def post_feedback(request):
    time = get_time()
    if request.method == 'POST':
        idh_time = []
        p_id = request.POST.getlist('patient')
        for id in p_id:
            idh_time.append(request.POST.getlist('idh-time-' + id)) #0110
        setting = request.POST.getlist('setting')
        if len(request.POST.getlist("bands")) > 0:
            bands = request.POST.getlist("bands")[0].split(',')
            empNo = request.POST.getlist("nurseId")[0]
            for index, id in enumerate(p_id):
                dialysis = Dialysis.objects.get(d_id=setting[index])
                f = Feedback(d_id=dialysis, 
                             idh_time=idh_time[index], 
                             empNo=empNo) 
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

# 警示表單
def warning_click(request):
    print("Warning click")
    click_time = datetime.now() # 點掉閃爍
    if request.method == 'POST':
        pBed = request.POST.get('patientBed')
        pName = request.POST.get('patientName')
        empNo = request.POST.get('empNo')
    try:
        w = Warnings(click_time=click_time, empNo=empNo, p_bed=pBed, p_name=pName)
        w.save()
        return JsonResponse({"status": 'success'})
    except Exception as error:
        return JsonResponse({"status": 'fail', "msg": str(error)})

def warning_feedback(request):
    # 1210改
    if request.method == 'POST':
        dismiss_time = datetime.now() # 0312 紀錄血壓
        pBed = request.POST.get('patientBed')
        pName = request.POST.get('patientName')
        empNo = request.POST.get('empNo')
        warning_SBP = request.POST.get('SBP')
        warning_DBP = request.POST.get('DBP')
        # 症狀
        is_sign = True if request.POST.get('sign-') == '1' else False
        # 口服藥物
        drug_midodrine = request.POST.get('drug-midodrine')
        drug_other = request.POST.get('drug-other-check')
        drug_all = [i for i in [drug_midodrine, drug_other] if i is not None]
        is_drug = True if len(drug_all) > 0 else False
        # 針劑藥物
        inject_IV_Glucose = request.POST.get('drug-IV_Glucose')
        inject_other = request.POST.get('inject-other-check')
        inject_all = [i for i in [inject_IV_Glucose, inject_other] if i is not None]
        is_inject = True if len(inject_all) > 0 else False
        # 調整透析設定
        setting_low_blood_flow = request.POST.get('setting-low_blood_flow')
        setting_low_UF = request.POST.get('setting-low_UF')
        setting_low_dialysate_flow = request.POST.get('setting-low_dialysate_flow')
        setting_other = request.POST.get('setting-other-check')
        setting_all = [i for i in [setting_low_blood_flow, setting_low_UF, setting_low_dialysate_flow, setting_other] if i is not None]
        is_setting = True if len(setting_all) > 0 else False
        # 護理處置
        nursing_HLFH = request.POST.get('nursing-HLFH')
        nursing_low_temp = request.POST.get('nursing-low_temp')
        nursing_flush = request.POST.get('nursing-flush')
        nursing_other = request.POST.get('nursing-other-check')
        nursing_all = [i for i in [nursing_HLFH, nursing_low_temp, nursing_flush, nursing_other] if i is not None]
        is_nursing = True if len(nursing_all) > 0 else False
        # 其他處理
        other_observe = request.POST.get('other-observe')
        other_other = request.POST.get('other-other-check')
        other_all = [i for i in [other_observe, other_other] if i is not None]
        is_other = True if len(other_all) > 0 else False
        print("DRUG:", drug_all, is_drug)
        print("INJECT:", inject_all, is_inject)
        print("SETTING:", setting_all, is_setting)
        print("NURSING:", nursing_all, is_nursing)
        print("OTHER:", other_all, is_other)
        print(f'Dismiss: {dismiss_time} empNo: {empNo}, SBP: {warning_SBP}, DBP: {warning_DBP}, patientBed: {pBed}, patientName: {pName}')
        ws = Warnings.objects.filter(p_bed=pBed, p_name=pName)
        try:
            if len(ws) > 1:
                ws.order_by('-click_time')[0].update(empNo=empNo, 
                                                     warning_SBP=warning_SBP, 
                                                     warning_DBP=warning_DBP, 
                                                     dismiss_time=dismiss_time,
                                                     is_sign=is_sign, 
                                                     is_drug=is_drug, 
                                                     is_inject=is_inject, 
                                                     is_setting=is_setting, 
                                                     is_nursing=is_nursing, 
                                                     is_other=is_other, 
                                                     drug_all=drug_all,
                                                     inject_all=inject_all,
                                                     setting_all=setting_all,
                                                     nursing_all=nursing_all,
                                                     other_all=other_all)
            elif len(ws) == 1:
                ws.update(empNo=empNo, 
                          warning_SBP=warning_SBP, 
                          warning_DBP=warning_DBP, 
                          dismiss_time=dismiss_time,
                          is_sign=is_sign, 
                          is_drug=is_drug, 
                          is_inject=is_inject, 
                          is_setting=is_setting, 
                          is_nursing=is_nursing, 
                          is_other=is_other, 
                          drug_all=drug_all,
                          inject_all=inject_all,
                          setting_all=setting_all,
                          nursing_all=nursing_all,
                          other_all=other_all)
            else:
                w = Warnings(empNo=empNo, 
                             p_bed=pBed, 
                             p_name=pName, 
                             warning_SBP=warning_SBP, 
                             warning_DBP=warning_DBP, 
                             click_time=dismiss_time, 
                             dismiss_time=dismiss_time,
                             is_sign=is_sign, 
                             is_drug=is_drug, 
                             is_inject=is_inject, 
                             is_setting=is_setting, 
                             is_nursing=is_nursing, 
                             is_other=is_other, 
                             drug_all=drug_all,
                             inject_all=inject_all,
                             setting_all=setting_all,
                             nursing_all=nursing_all,
                             other_all=other_all)
                w.save()
            print("Success update warning")
            return JsonResponse({"status": 'success'})
        except Exception as error:
            return JsonResponse({"status": 'fail', "msg": str(error)})

# 護理師專區
def get_nurse_patients(bed_list):
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

# 輸出報表
def export_file(request):
    '''0109 Export patient data to Excel file'''
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')
    if start_time != '' and end_time != '':
        print("start time:", start_time, ", end time: ", end_time)
        start_time = datetime.strptime(str(start_time), "%Y-%m-%dT%H:%M")
        end_time = datetime.strptime(str(end_time), "%Y-%m-%dT%H:%M")
        # Create the export view 
        filename = 'PatientData.xlsx'
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        wb = Workbook()
        ws = wb.active
        ws.title = "all_record"
        ws.append(["員工號", "姓名", "床位", "警示關閉時間", "SBP", "DBP", "填寫時間",
                   "口服藥物", "針劑藥物", "調整透析設定", "護理處置", "其他處理"])
        warnings = Warnings.objects.filter(dismiss_time__gte=start_time, dismiss_time__lte=end_time)
        if len(warnings) != 0:
            for warning in warnings:
                data = [warning.empNo, warning.p_name, warning.p_bed, warning.click_time, warning.warning_SBP, warning.warning_DBP, warning.dismiss_time,
                        warning.drug_all, warning.inject_all, warning.setting_all, warning.nursing_all, warning.other_all]
                ws.append(data)
        # Save the workbook to the HttpResponse
        wb.save(response)
        print("Success exporting file", response)
        return response
    else:
        return HttpResponse("請提供有效的起始時間和結束時間")

def corn_job():
    fetchData()
    print("Successfully fetch API")
    splitCSV()
    print("Successfully split to 3 CSV files")
    saveData()
    print("[corn_job]Successfully save new data to database")