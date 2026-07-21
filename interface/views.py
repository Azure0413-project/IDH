from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
import datetime
from datetime import datetime, timedelta
from interface.models import Patient, Dialysis, Record, Feedback, Predict, Warnings, Nurse
from django.core import serializers
from django.db.models import Max
from django.db import transaction # 260717 add a packages to store data
from interface.model.prediction import predict_idh
from scripts.fetch_API import fetchData
from scripts.DBbuilder import splitCSV
from scripts.load_data import saveData
from decimal import Decimal
import numpy as np
from openpyxl import Workbook
import sqlite3
from django.utils import timezone

# 在 views.py 最上方加入這行
import base64
from django.contrib.auth import authenticate, login
import logging


# 建立 logger 實例
logger = logging.getLogger(__name__)
# Create your views here.
now = timezone.now()
print("Now is:", now)
b_area = ['B5', 'B9', 'B3', 'B8', 'B2', 'B7', 'B1', 'B6']
c_area = ['C5', 'C9', 'C3', 'C8', 'C2', 'C7', 'C1', 'C6']
d_area = ['D5', 'D9', 'D3', 'D8', 'D2', 'D7', 'D1', 'D6']
a_area = ['A9', '', 'A5', '', 'A3', 'A8', 'A2', 'A7', 'A1', 'A6']
e_area = ['', '', 'E5', 'E8', 'E3', 'E7', 'E2', 'E6', 'E1', '']
i_area = ['', '', 'I2', '', 'I1', '']

def get_time():
    # now = False
    now = True #push要改True
    if now:
        time = datetime.now()
    else:
        time = datetime(2026, 3, 18, 13, 6, 0)
        # time = datetime(2026, 1, 28, 10, 0, 0)
    return time

def index(request, area="dashboard"):

    # ===== 測試 Watchdog 專用 (測完請刪除) (Test watchdog)=====
    # print("故意卡住 15 秒...")
    # time.sleep(15) 
    # =======================================

    time = get_time() #push要開
    if area == "dashboard" and time.minute % 3 == 0: #push要開
        corn_job()  #push要開                     
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
        corn_job() 
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
        all_idh_previous = [0]
        do_pred = False
    else:
        # all_preds = Predict.objects.all()
        # for p in all_preds[:32]:
        #     print(p.pred_id, p.d_id, p.flag, p.pred_time, p.pred_idh)
        # print(f"now_dialysis: {now_dialysis},\n len: {len(now_dialysis)}")
        preds = Predict.objects.filter(d_id=now_dialysis[0].d_id).order_by('pred_time').reverse()
        # print(f"\npred: {preds}\n len: {len(preds)}")
        
        last_pred = datetime.min if len(preds) == 0 else preds[0].pred_time
        
        if datetime.now() >= last_pred + timedelta(minutes=60):
            do_pred = True
            all_idh = predict_idh()
            print("[prediction]", time)
            
            # 修正：檢查 preds 是否為空
            if len(preds) > 0:
                same_preds = Predict.objects.filter(
                    pred_time__date=preds[0].pred_time.date(), 
                    pred_time__hour=preds[0].pred_time.hour
                ).order_by('flag')
                all_pred_idh = [s.pred_idh for s in same_preds]
                all_idh_previous = [np.float32(a) for a in all_pred_idh] if all_pred_idh else [0]
            else:
                all_idh_previous = [0]
        else:
            do_pred = False
            # 修正：檢查 preds 是否為空
            if len(preds) > 0:
                same_preds = Predict.objects.filter(
                    pred_time__date=preds[0].pred_time.date(), 
                    pred_time__hour=preds[0].pred_time.hour
                ).order_by('flag')
                all_pred_idh = [s.pred_idh for s in same_preds]
                all_idh = [np.float32(a) for a in all_pred_idh] if all_pred_idh else [0]
                all_idh_previous = [np.float32(a) for a in all_pred_idh] if all_pred_idh else [0]
            else:
                all_idh = [0]
                all_idh_previous = [0]
    
    flag = 0
    all_area = [a_area, b_area, c_area, d_area, e_area, i_area]
    all_patients = [a_patients, b_patients, c_patients, d_patients, e_patients, i_patients]
    
    # print(f"all_idh: {all_idh}, len: {len(all_idh)}\n")
    for a in range(len(all_area)):
        for index, bed in enumerate(all_area[a]):
            patient = {'bed': bed, 'idh': 0}
            
            for d in now_dialysis:
                if bed == d.bed:
                    start_time = d.start_time
                    
                    # 修正：使用 try-except 或 first() 方法
                    try:
                        patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
                    except IndexError:
                        patient['id'] = '---'
                        continue
                    
                    patient['setting'] = d
                    r = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time).order_by('record_time')
                    
                    if len(r) == 0:
                        patient['id'] = '---'
                        continue
                    else:
                        patient['record'] = r[len(r) - 1]
                    
                    # 修正：檢查 flag 是否超出 all_idh 的範圍
                    if flag < len(all_idh) and flag < len(all_idh_previous):
                        if time.minute == 30:
                            patient['idh'] = int(round(all_idh[flag] * 100))
                        else:
                            patient['idh'] = max(
                                int(all_idh_previous[flag] * 100),
                                int(round(all_idh[flag] * 100))
                            )
                    else:
                        # print(f"flag: {flag} all_idh: {len(all_idh)}, all_idh_previous: {len(all_idh_previous)} \n")
                        patient['idh'] = 0
                    
                    patient['random_code'] = d.random_code

                    # ========== EBM 預測區塊開始 ==========
                    # print(f"\n[EBM DEBUG] 檢查 Dialysis {d.d_id} (Bed: {bed}, Patient: {d.p_id.p_name})")
                    # if(d.d_id == 61328):
                    #     print(Record.objects.filter(d_id=d.d_id).order_by('record_time'))
                    #     print(Record.objects.filter(d_id=d.d_id).order_by('record_time').last())
                    

                    # 判斷是否為新透析：檢查第一筆 Record 的時間
                    ENABLE_EBM_LOGS = True
                    first_record = Record.objects.filter(d_id=d.d_id).order_by('record_time').last()
                    
                    ebm_warning = False  # 預設不顯示警告
                    ebm_prob = 0.0
                    
                    if first_record:
                        time_since_first_record = (datetime.now() - first_record.record_time).total_seconds()
                        minutes_ago = time_since_first_record / 60
                        
                        # print(f"[EBM DEBUG] - First record time: {first_record.record_time}")
                        # print(f"[EBM DEBUG] - Time since first record: {minutes_ago:.1f} 分鐘前")
                        # print(f"[EBM DEBUG] - Random code: {d.random_code}")
                        
                        # 如果第一筆記錄在最近 30 分鐘內，認為是新透析
                        if time_since_first_record < 1800:  # 30分鐘 = 1800秒
                            # print(f"[EBM DEBUG] ✓ 符合時間窗口（< 30分鐘）")
                            
                            # 檢查是否已經預測過（查詢 Predict 表，避免重複）
                            ebm_predicted = Predict.objects.filter(
                                d_id=d.d_id,
                                flag=-1  # 用 -1 標記 EBM 預測
                            ).exists()
                            
                            # print(f"[EBM DEBUG] - 已預測過: {ebm_predicted}")
                            
                            if not ebm_predicted:
                                # print(f"[EBM DEBUG] → 開始執行 EBM 預測...")
                                try:
                                    from interface.model.EBM import predict_idh_ebm
                                    ebm_prob = predict_idh_ebm(d.d_id, use_database_flag=False)
                                    
                                    # 判斷是否顯示警告：預測 >= 0.85 且 random_code == 1
                                    if ebm_prob >= 0.85 and d.random_code == 1:
                                        ebm_warning = True
                                    
                                    # print(f"[EBM RESULT] Dialysis {d.d_id}: prob={ebm_prob:.4f} ({int(ebm_prob*100)}%), warning={ebm_warning}")
                                    if ENABLE_EBM_LOGS:
                                        print(f"--------------------------------------------------")
                                        print(f"[EBM NEW PREDICTION] Time: {datetime.now().strftime('%H:%M:%S')}")
                                        print(f"  Bed: {bed} | ID: {d.d_id} | RandomCode: {d.random_code}")
                                        print(f"  Result: {ebm_prob:.4f} ({int(ebm_prob*100)}%)")
                                        print(f"  Warning Triggered: {ebm_warning}")
                                        print(f"--------------------------------------------------")
                                except Exception as e:
                                    print(f"[EBM ERROR] Prediction failed for dialysis {d.d_id}: {e}")
                                    import traceback
                                    traceback.print_exc()
                            else:
                                print(f"[EBM DEBUG] ✗ 跳過（已預測過）")
                        else:
                            print(f"[EBM DEBUG] ✗ 不符合時間窗口（{minutes_ago:.1f} 分鐘前 > 30分鐘）")
                    else:
                        print(f"[EBM DEBUG] ✗ 沒有 Record 資料")
                    
                    # 傳遞到前端
                    patient['ebm_warning'] = ebm_warning
                    patient['ebm_prob'] = int(round(ebm_prob * 100))  # 轉換成百分比
                    # ========== EBM 預測區塊結束 ==========

                    
                    # First click logic
                    w = Warnings.objects.filter(p_bed=bed).order_by('click_time').reverse()
                    if len(w) == 0:
                        patient['first_click'] = False 
                    else:
                        last_half_hour = time.replace(minute=30, second=0, microsecond=0)
                        if time.minute < 30:
                            last_half_hour -= timedelta(hours=1)
                        patient['first_click'] = w[0].click_time >= last_half_hour
                    
                    # Warning feedback logic
                    w = Warnings.objects.filter(p_bed=bed).order_by('dismiss_time').reverse()

                    # First, determine if the original conditions would make it False
                    should_be_false = False

                    if len(w) == 0 or w[0].dismiss_time == None:
                        should_be_false = True
                    else:
                        last_half_hour = time.replace(minute=30, second=0, microsecond=0)
                        if time.minute < 30:
                            last_half_hour -= timedelta(hours=1)
                        should_be_false = w[0].dismiss_time < last_half_hour

                    # Apply the additional time condition
                    if should_be_false and 30 <= time.minute <= 35:
                        patient['done_warning'] = False
                    elif not should_be_false:
                        patient['done_warning'] = True

                    # ==========================================
                    # 🚨 測試專用程式碼：強制覆蓋數值製造假警報 (測試完請刪除)
                    # ==========================================
                    # patient['idh'] = 95             # 強制 IDH > 85
                    # patient['random_code'] = 1      # 強制設為 1
                    # patient['done_warning'] = False # 強制設為未處置
                    # patient['first_click'] = False  # 強制設為未點擊
                    # if 'record' in patient and patient['record']:
                    #     patient['record'].SBP = 80  # 強制血壓低於 90，讓病床亮紅燈
                    # ==========================================
        
                    # 修正：檢查 flag 是否超出 all_idh 的範圍
                    if do_pred and flag < len(all_idh):
                        dialysis = Dialysis.objects.get(d_id=d.d_id)
                        pred = Predict(d_id=dialysis, flag=flag, pred_idh=Decimal(str(all_idh[flag])))
                        pred.save()
                    
                    # print(f"Patient: {bed}, idh: {patient['idh']}, flag:{flag} \n")
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
    
    d = Dialysis.objects.filter(bed=bed, start_time__lte=time, end_time__gte=time).first()

    if d:
        # Continue with your logic using 'd'
        pass 
    else:
        # Handle the case where no patient is found (e.g., return an error message or blank data)
        print(f"No active dialysis session found for bed {bed} at {time}")
        return redirect('/index/dashboard')

    start_time = d.start_time
    # patient data
    try:
        patient['id'] = Patient.objects.filter(p_id=d.p_id.p_id)[0]
    except IndexError:
        # Fallback if patient ID is missing
        patient['id'] = {'p_name': 'Unknown', 'p_id': d.p_id.p_id}

    
    # latest dialysis information
    patient['setting'] = d
    
    # latest dialysis record
    r_today = Record.objects.filter(d_id=d.d_id, record_time__gte=start_time, record_time__lte=time).order_by('record_time')
    patient['record'] = r_today.last() if r_today.exists() else None

    # all record
    all_dialysis = Dialysis.objects.filter(p_id=d.p_id.p_id, times__gte=d.times-2)
    temp = []
    for dialysis in all_dialysis:
        record_list = Record.objects.filter(d_id=dialysis.d_id, record_time__lte=time).select_related().order_by('record_time')
        for record in record_list:
            # 先檢查是否為 None，如果是 None 或小於等於 0，都顯示為 '-'
            if record.d_id.temperature is None or record.d_id.temperature <= 0: 
                record.d_id.temperature = '-'
            
            # 同樣檢查 start_temperature
            if record.d_id.start_temperature is None or record.d_id.start_temperature <= 0: 
                record.d_id.start_temperature = '-'
            
            if record.d_id.ESA == str(-1): record.d_id.ESA = '-'
            
            # flush 也建議做同樣的檢查，以防萬一
            if record.flush is None or record.flush == -1.000: 
                record.flush = '-'
            
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
    timestamp = str(d.start_time.strftime("%Y-%m-%d %H:%M"))

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
        logger.info(f"[WARNING CLICK] bed={pBed}, name={pName}, empNo={empNo}, time={click_time}")
        return JsonResponse({"status": 'success'})
    except Exception as error:
        logger.error(f"[warning_click] failed: {error}", exc_info=True)
        return JsonResponse({"status": 'fail', "msg": str(error)})

def warning_feedback(request):
    # 1210改
    # index,html nurseAreaSearch.html
    # POST.get(name)
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
        # 護理師處置時間
        handle_time = request.POST.get('handle-time')
        
        
        print("HANDLE TIME:",handle_time)
        print("DRUG:", drug_all, is_drug)
        print("INJECT:", inject_all, is_inject)
        print("SETTING:", setting_all, is_setting)
        print("NURSING:", nursing_all, is_nursing)
        print("OTHER:", other_all, is_other)
        print(f'Dismiss: {dismiss_time} empNo: {empNo}, SBP: {warning_SBP}, DBP: {warning_DBP}, patientBed: {pBed}, patientName: {pName}')
        ws = Warnings.objects.filter(p_bed=pBed, p_name=pName)
        try:
            if len(ws) > 1:
                if len(ws) > 1:
                    obj = ws.order_by('-click_time')[0]
                    obj.empNo = empNo
                    obj.warning_SBP = warning_SBP
                    obj.warning_DBP = warning_DBP
                    obj.dismiss_time = dismiss_time
                    obj.is_sign = is_sign
                    obj.is_drug = is_drug
                    obj.is_inject = is_inject
                    obj.is_setting = is_setting
                    obj.is_nursing = is_nursing
                    obj.is_other = is_other
                    obj.drug_all = drug_all
                    obj.inject_all = inject_all
                    obj.setting_all = setting_all
                    obj.nursing_all = nursing_all
                    obj.other_all = other_all
                    obj.handle_time = handle_time
                    obj.save()
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
                          other_all=other_all,
                          handle_time=handle_time)
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
                             other_all=other_all,
                             handle_time=handle_time)
                w.save()
            print("Success update warning")
            return JsonResponse({"status": 'success'})
        except Exception as error:
            logger.error(f"[warning_feedback] save failed: bed={pBed}, name={pName}, err={error}", exc_info=True)
            return JsonResponse({"status": 'fail', "msg": str(error)})
    else:
        return JsonResponse({"status": 'fail', "msg": "Only POST allowed"}, status=405)

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
                        warning.drug_all, warning.inject_all, warning.setting_all, warning.nursing_all, warning.other_all,warning.handle_time]
                ws.append(data)
        # Save the workbook to the HttpResponse
        wb.save(response)
        print("Success exporting file", response)
        return response
    else:
        return HttpResponse("請提供有效的起始時間和結束時間")

# 資料庫
def database(request):
    print("Request received at database view")  # Debug statement
    selected_table = request.GET.get('table', 'interface_feedback')
    db_data = None
    
    if selected_table:
        try:
            # Use a context manager to ensure the connection is properly closed
            with sqlite3.connect('db.sqlite3', timeout=10) as conn:
                cursor = conn.cursor()
                
                # Fetch data from the selected table
                cursor.execute(f'SELECT * FROM {selected_table}')
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                db_data = {'columns': columns, 'rows': rows}
                
            print(f"Successfully fetched data from {selected_table}")
        except Exception as e:
            print("Error loading database schema:", e)  # Debug statement
            return HttpResponse("Error loading database schema. Please check the console for details.")
    
    return render(request, 'database.html', {'db_data': db_data, 'selected_table': selected_table})

def corn_job():
    try:
        fetchData()
        print("Successfully fetch API")
        splitCSV()
        print("Successfully split to 3 CSV files")
        with transaction.atomic():
            saveData()
        print("[corn_job] Successfully save new data to database")
    except Exception as e:
        # This catches the ConnectTimeout and prints it to console, 
        # but allows the website to keep running.
        logger.error(f"[corn_job] failed: {e}", exc_info=True)

def custom_page_not_found(request, exception):
    # 1. 記錄錯誤：把錯誤的網址寫入 log 檔
    logger.warning(f"404 Error - Page not found. Requested URL: {request.path}")
    
    # 2. 自動導回首頁：這裡假設你的首頁是 '/index/dashboard'
    return redirect('/index/dashboard')