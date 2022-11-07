import csv
import pandas as pd

class CSV:
    def __init__(self, path):
        self.file = path

    def read_to_patient(self):
        usecols= ['ID', '姓名', '性別', '出生年月日']
        df = pd.read_csv(self.file, usecols=usecols)
        df = df.drop_duplicates()                     # drop duplicates
        df.to_csv('data/patient.csv', encoding='utf_8_sig')    
    
    def read_to_dialysis(self):
        usecols = ['ID', '年齡', '透析次數(本院)', '透析開始時間', '透析結束時間', '透析機編號', '床位', '體溫', '開始體溫', '透析前體重(kg)', '理想體重(kg)', '目標脫水量(L)', '輸液量(L)' , '食物重量(kg)', '預估脫水量(L)', '設定脫水量(L)', '結束體重(kg)', '實際脫水量(L)', 'Start_SBP', 'Start_DBP', 'End_SBP', 'End_DBP', '透析模式', '透析器', '開始透析液流速', '開始血液流速', '透析液Ca：3.0', '傳導度：13.9', '血管通路', 'Heparin', 'ESA', '透析器凝血情況']
        df = pd.read_csv(self.file, usecols=usecols)
        df = df.drop_duplicates()                     # drop duplicates
        df.to_csv('data/dialysis.csv', encoding='utf_8_sig') 

    def read_to_record(self):
        usecols = ['ID', '透析次數(本院)', '透析次數(本院)', '血壓(收縮)', '血壓(舒張)', '脈搏', '呼吸', '血流速(ml/min)', '透析液流速(ml/min)', '靜脈壓(mmHg)', '透析液壓(mmHg)', '膜上壓(mmHg)', '脫水速率', '累積量', '透析液溫度(℃)', '肝素注射量(ml/hr)', '沖水量(L)', '確認血管通路']
        df = pd.read_csv(self.file, usecols=usecols)
        df = df.drop_duplicates()                     # drop duplicates
        df.to_csv('data/record.csv', encoding='utf_8_sig') 

data = CSV('data/202111-202207.csv')
data.read_to_patient()
data.read_to_dialysis()
data.read_to_record()