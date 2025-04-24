import csv
from interface.models import Patient, Dialysis, Record
from decimal import Decimal
import datetime
from datetime import datetime, timedelta
from random import randint

def run():
    patient_path = 'interface/data/patient.csv'
    dialysis_path = 'interface/data/dialysis.csv'
    record_path = 'interface/data/record.csv'
    with open(patient_path, "r", encoding='utf-8') as csv_file:
        data = csv.reader(csv_file, delimiter=",")
        next(data)                                            # 跳過第一列
        patients = []
        for row in data:
            patient = Patient(
                p_id = row[1],
                p_name = row[2],
                gender = row[3],
                birth = row[4] 
            )
            if not Patient.objects.filter(p_id=patient.p_id).exists():                
                patients.append(patient)
            if len(patients) > 100:
                Patient.objects.bulk_create(patients)         # 減少儲存次數
                patients = []
        if patients:
            Patient.objects.bulk_create(patients)
    with open(dialysis_path, "r", encoding='utf-8') as csv_file:
        data = csv.reader(csv_file, delimiter=",")
        next(data)
        dialysis = []
        for row in data:
            if row[5] == "-1":
                end_time = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S") + timedelta(hours=4)
            else:
                end_time = row[5]
            dialyse = Dialysis(
                p_id = Patient.objects.get(p_id = row[1]),
                age = row[2],
                times = row[3],
                start_time = row[4],
                end_time = end_time,
                machine_id = row[6],
                bed = row[7],
                temperature = Decimal(row[8]),
                start_temperature = Decimal(row[9]),
                before_weight = Decimal(row[10]),
                ideal_weight = Decimal(row[11]),
                expect_dehydration = Decimal(row[12]),
                transfusion = Decimal(row[13]),
                food = Decimal(row[14]),
                estimate_dehydration = Decimal(row[15]),
                set_dehydration = Decimal(row[16]),
                after_weight = Decimal(row[17]),
                real_dehydration = Decimal(row[18]),
                start_SBP = Decimal(row[19]),
                start_DBP = Decimal(row[20]),
                end_SBP = Decimal(row[21]),
                end_DBP = Decimal(row[22]),
                mode = row[23],
                machine = row[24],
                start_flow_speed = Decimal(row[25]),
                start_blood_speed = Decimal(row[26]),
                Ca = Decimal(row[27]),
                conductivity = Decimal(row[28]),
                channel = row[29],
                heparin = row[30],
                ESA = row[31],
                coagulation = row[32],
                # change it back to randint(0,1)
                random_code = randint(1)
            )
            if not Dialysis.objects.filter(p_id=dialyse.p_id, times=dialyse.times).exists():                
                dialysis.append(dialyse)
        if len(dialysis) > 5000:
            Dialysis.objects.bulk_create(dialysis)   
            dialysis = []
        if dialysis:
            Dialysis.objects.bulk_create(dialysis)
    with open(record_path, "r", encoding='utf-8') as csv_file:
        data = csv.reader(csv_file, delimiter=",")
        next(data)                                            # 跳過第一列
        records = []
        for row in data:
            d_id = Dialysis.objects.filter(p_id = row[1], times = row[2])
            if d_id.count() > 1:
                d_id = d_id[d_id.count() - 1]
            else:
                d_id = d_id[0]
            record = Record(
                d_id = d_id,
                record_time = row[3],
                SBP = Decimal(row[4]),
                DBP = Decimal(row[5]),
                pulse = Decimal(row[6]),
                breath = Decimal(row[7]),
                blood_speed = Decimal(row[8]),
                flow_speed = Decimal(row[9]),
                CVP = Decimal(row[10]),
                DP = Decimal(row[11]),
                TMP = Decimal(row[12]),
                dehydrate_speed = Decimal(row[13]),
                accumulation = Decimal(row[14]),
                dialyse_temperature = Decimal(row[15]),
                heparin_volume = Decimal(row[16]),
                flush = row[17],
                channel_confirmed = row[18],
            )            
            if not Record.objects.filter(d_id=record.d_id, record_time=record.record_time).exists():                
                records.append(record)
            if len(records) > 5000:
                Record.objects.bulk_create(records)         # 減少儲存次數
                records = []
        if records:
            Record.objects.bulk_create(records)

def saveData():
    run()