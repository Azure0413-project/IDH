# import csv
# from interface.models import Patient, Dialysis, Record
# from decimal import Decimal
# import datetime
# from datetime import datetime, timedelta
# from random import randint

# def run():
#     patient_path = 'interface/data/patient.csv'
#     dialysis_path = 'interface/data/dialysis.csv'
#     record_path = 'interface/data/record.csv'
#     with open(patient_path, "r", encoding='utf-8') as csv_file:
#         data = csv.reader(csv_file, delimiter=",")
#         next(data)                                            # 跳過第一列
#         patients = []
#         for row in data:
#             # Ryan 26.01.28
#             patient = Patient(
#                 p_id = row['ID'],
#                 p_name = row['姓名'],
#                 gender = row['性別'],
#                 birth = row['出生年月日']
#             )
#             if not Patient.objects.filter(p_id=patient.p_id).exists():                
#                 patients.append(patient)
#             if len(patients) > 100:
#                 Patient.objects.bulk_create(patients)         # 減少儲存次數
#                 patients = []
#         if patients:
#             Patient.objects.bulk_create(patients)
#     with open(dialysis_path, "r", encoding='utf-8') as csv_file:
#         data = csv.reader(csv_file, delimiter=",")
#         next(data)
#         dialysis = []
#         for row in data:
#             if row[5] == "-1":
#                 end_time = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S") + timedelta(hours=4)
#             else:
#                 end_time = row[5]
#             dialyse = Dialysis(
#                 p_id = Patient.objects.get(p_id = row[1]),
#                 age = row[2],
#                 times = row[3],
#                 start_time = row[4],
#                 end_time = end_time,
#                 machine_id = row[6],
#                 bed = row[7],
#                 temperature = Decimal(row[8]),
#                 start_temperature = Decimal(row[9]),
#                 before_weight = Decimal(row[10]),
#                 ideal_weight = Decimal(row[11]),
#                 expect_dehydration = Decimal(row[12]),
#                 transfusion = Decimal(row[13]),
#                 food = Decimal(row[14]),
#                 estimate_dehydration = Decimal(row[15]),
#                 set_dehydration = Decimal(row[16]),
#                 after_weight = Decimal(row[17]),
#                 real_dehydration = Decimal(row[18]),
#                 start_SBP = Decimal(row[19]),
#                 start_DBP = Decimal(row[20]),
#                 end_SBP = Decimal(row[21]),
#                 end_DBP = Decimal(row[22]),
#                 mode = row[23],
#                 machine = row[24],
#                 start_flow_speed = Decimal(row[25]),
#                 start_blood_speed = Decimal(row[26]),
#                 Ca = Decimal(row[27]),
#                 conductivity = Decimal(row[28]),
#                 channel = row[29],
#                 heparin = row[30],
#                 ESA = row[31],
#                 coagulation = row[32],
#                 random_code = randint(0, 1)
#             )
#             if not Dialysis.objects.filter(p_id=dialyse.p_id, times=dialyse.times).exists():                
#                 dialysis.append(dialyse)
#         if len(dialysis) > 5000:
#             Dialysis.objects.bulk_create(dialysis)   
#             dialysis = []
#         if dialysis:
#             Dialysis.objects.bulk_create(dialysis)
#     with open(record_path, "r", encoding='utf-8') as csv_file:
#         data = csv.reader(csv_file, delimiter=",")
#         next(data)                                            # 跳過第一列
#         records = []
#         for row in data:
#             d_id = Dialysis.objects.filter(p_id = row[1], times = row[2])
#             if d_id.count() > 1:
#                 d_id = d_id[d_id.count() - 1]
#             else:
#                 d_id = d_id[0]
#             record = Record(
#                 d_id = d_id,
#                 record_time = row[3],
#                 SBP = Decimal(row[4]),
#                 DBP = Decimal(row[5]),
#                 pulse = Decimal(row[6]),
#                 breath = Decimal(row[7]),
#                 blood_speed = Decimal(row[8]),
#                 flow_speed = Decimal(row[9]),
#                 CVP = Decimal(row[10]),
#                 DP = Decimal(row[11]),
#                 TMP = Decimal(row[12]),
#                 dehydrate_speed = Decimal(row[13]),
#                 accumulation = Decimal(row[14]),
#                 dialyse_temperature = Decimal(row[15]),
#                 heparin_volume = Decimal(row[16]),
#                 flush = row[17],
#                 channel_confirmed = row[18],
#             )            
#             if not Record.objects.filter(d_id=record.d_id, record_time=record.record_time).exists():                
#                 records.append(record)
#             if len(records) > 5000:
#                 Record.objects.bulk_create(records)         # 減少儲存次數
#                 records = []
#         if records:
#             Record.objects.bulk_create(records)

# def saveData():
#     run()

import csv
import os
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
from random import randint

from interface.models import Patient, Dialysis, Record
from django.db import IntegrityError


# =========================
# 共用工具
# =========================

def log(level, msg):
    print(f"[{level}] {msg}")


def check_csv_file(path):
    if not os.path.exists(path):
        log("ERROR", f"CSV not found: {path}")
        return False
    if os.path.getsize(path) == 0:
        log("ERROR", f"CSV is empty: {path}")
        return False
    return True


def to_decimal(value, field, row):
    try:
        if value in ("", None, "-1"):
            return None
        return Decimal(value)
    except InvalidOperation:
        log("WARN", f"Decimal parse failed [{field}] value={value} row={row}")
        return None


# =========================
# 主程式
# =========================

def run():

    patient_path  = "interface/data/patient.csv"
    dialysis_path = "interface/data/dialysis.csv"
    record_path   = "interface/data/record.csv"

    # --------------------------------------------------
    # Patient
    # 原 index:
    # 0: ID, 1: 姓名, 2: 性別, 3: 出生年月日
    # --------------------------------------------------
    if check_csv_file(patient_path):
        with open(patient_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            required = ['ID', '姓名', '性別', '出生年月日']
            if not set(required).issubset(reader.fieldnames):
                log("ERROR", f"patient.csv missing columns: {set(required) - set(reader.fieldnames)}")
            else:
                patients = []
                for row in reader:
                    try:
                        if not row['ID']:
                            log("SKIP", f"patient missing ID: {row}")
                            continue

                        patient = Patient(
                            p_id   = row['ID'],          # 原 row[0]
                            p_name = row['姓名'],        # 原 row[1]
                            gender = row['性別'],        # 原 row[2]
                            birth  = row['出生年月日'],  # 原 row[3]
                        )

                        if not Patient.objects.filter(p_id=patient.p_id).exists():
                            patients.append(patient)

                        if len(patients) >= 100:
                            Patient.objects.bulk_create(patients)
                            patients.clear()

                    except Exception as e:
                        log("ERROR", f"patient row failed: {row} err={e}")

                if patients:
                    Patient.objects.bulk_create(patients)

    # --------------------------------------------------
    # Dialysis
    # 原 index 備註寫在每個欄位後
    # --------------------------------------------------
    if check_csv_file(dialysis_path):
        with open(dialysis_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            dialysis_list = []

            for row in reader:
                try:
                    patient = Patient.objects.filter(p_id=row['ID']).first()  # 原 row[1]
                    if not patient:
                        log("SKIP", f"dialysis patient not found: {row}")
                        continue

                    start_time = datetime.fromisoformat(row['透析開始時間'])  # 原 row[4]
                    end_time = (
                        start_time + timedelta(hours=4)
                        if row.get('透析結束時間') in ("", "-1", None)
                        else datetime.fromisoformat(row['透析結束時間'])
                    )

                    dial = Dialysis(
                        p_id = patient,
                        age = row.get('年齡'),
                        times = row.get('透析次數(本院)'),
                        start_time = start_time,
                        end_time = end_time,
                        machine_id = row.get('透析機編號'),  # 請確認 CSV 標頭是 '機器ID' 還是 '透析機編號'
                        bed = row.get('床位'),
                        
                        # --- 數值類 (使用 to_decimal 轉換) ---
                        temperature = to_decimal(row.get('溫度'), '溫度', row),
                        start_temperature = to_decimal(row.get('開始體溫'), '開始體溫', row), # 原版 row[9]
                        before_weight = to_decimal(row.get('透析前體重(kg)'), '透析前體重(kg)', row),
                        ideal_weight = to_decimal(row.get('理想體重(kg)'), '理想體重(kg)', row),
                        expect_dehydration = to_decimal(row.get('預估脫水量(L)'), '預估脫水量(L)', row), # 原版 row[12]
                        transfusion = to_decimal(row.get('輸液量(L)'), '輸液量(L)', row), # 原版 row[13]
                        food = to_decimal(row.get('食物重量(kg)'), '食物重量(kg)', row), # 原版 row[14]
                        estimate_dehydration = to_decimal(row.get('設定脫水量(L)'), '設定脫水量(L)', row), # 原版 row[15] (注意Key可能是設定或預估)
                        set_dehydration = to_decimal(row.get('設定脫水量(L)'), '設定脫水量(L)', row), # 原版 row[16]
                        after_weight = to_decimal(row.get('結束體重(kg)'), '結束體重(kg)', row),
                        real_dehydration = to_decimal(row.get('實際脫水量(L)'), '實際脫水量(L)', row),
                        
                        # --- 這裡就是導致報錯的關鍵漏失 (血壓與流速) ---
                        start_SBP = to_decimal(row.get('Start_SBP'), 'Start_SBP', row), # 原版 row[19]
                        start_DBP = to_decimal(row.get('Start_DBP'), 'Start_DBP', row), # 原版 row[20] -> 這裡報錯!
                        end_SBP = to_decimal(row.get('End_SBP'), 'End_SBP', row),       # 原版 row[21]
                        end_DBP = to_decimal(row.get('End_DBP'), 'End_DBP', row),       # 原版 row[22]
                        
                        start_flow_speed = to_decimal(row.get('開始透析液流速'), '開始透析液流速', row), # 原版 row[25]
                        start_blood_speed = to_decimal(row.get('開始血液流速'), '開始血液流速', row),   # 原版 row[26]
                        Ca = to_decimal(row.get('透析液Ca'), '透析液Ca', row),          # 原版 row[27]
                        conductivity = to_decimal(row.get('傳導度'), '傳導度', row),    # 原版 row[28]

                        # --- 字串類 (直接 get) ---
                        mode = row.get('透析模式'),          # 原版 row[23]
                        # machine = row.get('透析器'),       # 原版 row[24] (如果你 Model 有這個欄位的話)
                        channel = row.get('血管通路'),       # 原版 row[29]
                        heparin = row.get('Heparin'),       # 原版 row[30]
                        ESA = row.get('ESA'),               # 原版 row[31]
                        coagulation = row.get('透析器凝血情況'), # 原版 row[32]
                        
                        random_code = randint(0, 1)
                    )

                    if not Dialysis.objects.filter(p_id=patient, times=dial.times).exists():
                        dialysis_list.append(dial)

                    if len(dialysis_list) >= 1000:
                        Dialysis.objects.bulk_create(dialysis_list)
                        dialysis_list.clear()

                except Exception as e:
                    log("ERROR", f"dialysis row failed: {row} err={e}")

            if dialysis_list:
                Dialysis.objects.bulk_create(dialysis_list)

    # --------------------------------------------------
    # Record
    # 原 index:
    # 0: ID, 1: 透析次數, 2: 紀錄時間, 3: SBP, 4: DBP ...
    # --------------------------------------------------
    if check_csv_file(record_path):
        with open(record_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            records = []

            for row in reader:
                try:
                    dialysis = (
                        Dialysis.objects
                        .filter(p_id__p_id=row['ID'], times=row['透析次數(本院)'])
                        .order_by('-pk')
                        .first()
                    )
                    if not dialysis:
                        log("SKIP", f"record dialysis not found: {row}")
                        continue

                    record = Record(
                        d_id = dialysis,
                        record_time = row['紀錄時間'],               # 原 row[3]
                        SBP = to_decimal(row['血壓(收縮)'], 'SBP', row),
                        DBP = to_decimal(row['血壓(舒張)'], 'DBP', row),
                        pulse = to_decimal(row['脈搏'], 'pulse', row),
                        breath = to_decimal(row['呼吸'], 'breath', row),
                        blood_speed = to_decimal(row['血流速(ml/min)'], 'blood_speed', row),
                        flow_speed = to_decimal(row['透析液流速(ml/min)'], 'flow_speed', row),
                        CVP = to_decimal(row['靜脈壓(mmHg)'], 'CVP', row),
                        DP = to_decimal(row['透析液壓(mmHg)'], 'DP', row),
                        TMP = to_decimal(row['膜上壓(mmHg)'], 'TMP', row),
                        dehydrate_speed = to_decimal(row['脫水速率'], 'dehydrate_speed', row),
                        accumulation = to_decimal(row['累積量'], 'accumulation', row),
                        dialyse_temperature = to_decimal(row['透析液溫度(℃)'], 'dialyse_temperature', row),
                        heparin_volume = to_decimal(row['肝素注射量(ml/hr)'], 'heparin_volume', row),
                        flush = row.get('沖水量(L)'),
                        channel_confirmed = row.get('確認血管通路'),
                    )

                    if not Record.objects.filter(
                        d_id=dialysis,
                        record_time=record.record_time
                    ).exists():
                        records.append(record)

                    if len(records) >= 5000:
                        Record.objects.bulk_create(records)
                        records.clear()

                except Exception as e:
                    log("ERROR", f"record row failed: {row} err={e}")

            if records:
                Record.objects.bulk_create(records)


def saveData():
    log("INFO", "Start loading CSV to DB")
    run()
    log("INFO", "Load finished")
