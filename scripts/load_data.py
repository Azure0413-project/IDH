
from django.utils import timezone
import csv
from interface.models import Patient, Record

def run():
    start_time = timezone.now()
    file_path = 'interface/data/洗腎病人名單.csv'
    record_path = 'interface/data/202111-202207.csv'
    with open(file_path, "r", encoding='utf-8') as csv_file:
        data = list(csv.reader(csv_file, delimiter=","))
        for row in data[1:]:
            Patient.objects.create(
                p_id=row[0],
                p_name=row[1],
            )
    with open(file_path, "r", encoding='utf-8') as csv_file:
        data = list(csv.reader(csv_file, delimiter=","))
        for row in data[1:]:
            Record.objects.create(
                p_id = row[0],
                name = row[1],
                gender = row[2],
                birth = row[3],
                age = row[4],
                times = row[5],
                start_time =row[6],
                end_time = row[7],
                record_time = row[8],
                machine_id = row[9],
                bed = row[10],
                temperature = row[11],
                start_temperature = row[12],
                before_weight = row[13],
                ideal_weight = row[14],
                expect_dehydration = row[15],
                transfusion = row[16],
                food = row[17],
                estimate_dehydration = row[18],
                set_dehydration = row[19],
                after_weight = row[20],
                real_dehydration = row[21],
                start_SBP = row[22],
                start_DBP = row[23],
                end_SBP = row[24],
                end_DBP = row[25],
                mode = row[26],
                machine = row[27],
                start_flow_speed = row[28],
                start_blood_speed = row[29],
                Ca = row[30],
                conductivity = row[31],
                channel = row[32],
                heparin = row[33],
                ESA = row[34],
                coagulation = row[35],
                SBP = row[36],
                DBP = row[37],
                pulse = row[38],
                breath = row[39],
                blood_speed = row[40],
                flow_speed = row[41],
                CVP = row[42],
                DP = row[43],
                TMP = row[44],
                dehydrate_speed = row[45],
                accumulation = row[46],
                dialyse_temperature = row[47],
                heparin_volume = row[48],
                flush = row[49],
                channel_confirmed = row[50],
            )
    end_time = timezone.now()
    self.stdout.write(
        self.style.SUCCESS(
            f"Loading CSV took: {(end_time-start_time).total_seconds()} seconds."
        )
    )