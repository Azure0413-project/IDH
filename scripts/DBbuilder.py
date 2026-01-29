import pandas as pd
from datetime import datetime
import os
from pandas.errors import EmptyDataError

## Ryan 26.01.28
class CSV:
    def __init__(self, path):
        self.file = path

    def read_to_patient(self):
        usecols = ['ID', '姓名', '性別', '出生年月日']

        # 1️⃣ File existence
        if not os.path.exists(self.file):
            print(f"[WARN] patient source CSV not found: {self.file}")
            return

        # 2️⃣ File empty
        if os.path.getsize(self.file) == 0:
            print(f"[WARN] patient source CSV is empty: {self.file}")
            return

        try:
            df = pd.read_csv(self.file)

            # 3️⃣ Required columns check
            missing = set(usecols) - set(df.columns)
            if missing:
                print(f"[WARN] patient CSV missing columns: {missing}")
                return

            # 4️⃣ Column filtering
            df = df[usecols]

        except EmptyDataError:
            print(f"[WARN] patient CSV has no data: {self.file}")
            return
        except Exception as e:
            print(f"[ERROR] read_to_patient failed: {e}")
            return

        # 5️⃣ Date parsing (safe)
        df['出生年月日'] = pd.to_datetime(
            df['出生年月日'], errors='coerce'
        ).dt.date

        df = df.dropna(subset=['ID'])   # defensive
        df = df.drop_duplicates()

        df.to_csv(
            'interface/data/patient.csv',
            index=False,
            encoding='utf_8_sig'
        )

        print(f"[OK] patient.csv updated ({len(df)} rows)")    
    
    def read_to_dialysis(self):
        usecols = ['ID', '年齡', '透析次數(本院)', '透析開始時間', '透析結束時間', '透析機編號', '床位', '體溫', '開始體溫', '透析前體重(kg)', '理想體重(kg)', '目標脫水量(L)', '輸液量(L)' , '食物重量(kg)', '預估脫水量(L)', '設定脫水量(L)', '結束體重(kg)', '實際脫水量(L)', 'Start_SBP', 'Start_DBP', 'End_SBP', 'End_DBP', '透析模式', '透析器', '開始透析液流速', '開始血液流速', '透析液Ca：3.0', '傳導度：13.9', '血管通路', 'Heparin', 'ESA', '透析器凝血情況']
        df = pd.read_csv(self.file, usecols=usecols)
        df['透析開始時間'] = df['透析開始時間'].apply(lambda x: pd.to_datetime(x))
        df['透析結束時間'] = df['透析結束時間'].apply(lambda x: pd.to_datetime(x))
        # df['床位'] = df['床位'].apply(lambda x: x if x[0].isdigit() == False else x[::-1])   # reverse bed_id
        df = df.fillna(-1)
        df = df.drop_duplicates()                     # drop duplicates
        # print(df.info())
        df.to_csv('interface/data/dialysis.csv', encoding='utf_8_sig') 

    def read_to_record(self):
        usecols = ['ID', '透析次數(本院)', '紀錄時間', '血壓(收縮)', '血壓(舒張)', '脈搏', '呼吸', '血流速(ml/min)', '透析液流速(ml/min)', '靜脈壓(mmHg)', '透析液壓(mmHg)', '膜上壓(mmHg)', '脫水速率', '累積量', '透析液溫度(℃)', '肝素注射量(ml/hr)', '沖水量(L)', '確認血管通路']
        df = pd.read_csv(self.file, usecols=usecols)
        df['紀錄時間'] = df['紀錄時間'].apply(lambda x: pd.to_datetime(x))
        df['沖水量(L)'] = pd.to_numeric(df['沖水量(L)'],errors="coerce")
        df = df.fillna(-1)
        df = df.drop_duplicates()                     # drop duplicates
        # df.info()
        df.to_csv('interface/data/record.csv', encoding='utf_8_sig') 


def run():
    data = CSV('interface/data/temp.csv')
    data.read_to_patient()
    data.read_to_dialysis()
    data.read_to_record()

def splitCSV():
    data = CSV('interface/data/temp.csv')
    data.read_to_patient()
    data.read_to_dialysis()
    data.read_to_record()
