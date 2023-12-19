# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 15:36:33 2023

@author: iir
"""

import pandas as pd
import numpy as np
import torch
from interface.weights.transformer import *
import warnings
warnings.filterwarnings("ignore")
#%%
def Data_Preprocess(file_name):
    data = pd.read_csv(file_name, encoding='utf-8_sig', engine='python')
    if len(data) <= 1:
        return [0]
    temp = ['透析開始時間', '紀錄時間']
    for i in temp:
        data[i] = pd.to_datetime(data[i])
    
    sequential = ['血壓(收縮)', '血壓(舒張)', '透析液流速(ml/min)', '脫水速率', '脈搏', '呼吸', '血流速(ml/min)', '沖水量(L)', '透析液溫度(℃)']
    for i in sequential:
        data[i] = pd.to_numeric(data[i],errors='coerce')
    data = data.fillna(-1)

    #1205改: 只保留以一小時為間隔的資料
    first_record = data.groupby("ID")['紀錄時間'].min()
    len(data['ID'].unique())
    filtered_data = pd.DataFrame()
    for patient_id, first_time in first_record.items():
        # print(patient_id, end=' ')
        filtered_times = []
        patient_data = data[data['ID'] == patient_id]
        # print(len(patient_data), end=' ')
        for i in range(len(patient_data)):
            next_hour = first_time + pd.DateOffset(hours=i)
            closest_time = min(patient_data['紀錄時間'], key=lambda x: abs(x-next_hour))
            if closest_time not in filtered_times:
                filtered_times.append(closest_time)
        # print(len(filtered_times))
        patient_data = patient_data[patient_data['紀錄時間'].isin(filtered_times)]
        filtered_data = pd.concat([filtered_data, patient_data], axis=0)
    data = filtered_data.sort_index().reset_index(drop=True)
    #1205 ---

    # 計算time_step
    date = data['透析開始時間'][0]
    record_num = 0 # calculate同次透析第幾筆紀錄
    time_s = []
    time = []
    
    for i in range(len(data)):
        # 若屬於同一筆透析資料
        if (data['透析開始時間'][i] == date) : 
            record_num += 1
    
        else:
            date = data['透析開始時間'][i]
            record_num = 0
            # 當該次透析跑完開始計算時間差
            for j in range(len(time_s)):
                time.append(240 - (time_s[j] - time_s[0]).seconds / 60)
            time_s = []
        time_s.append(data['紀錄時間'][i])
    
    for j in range(len(time_s)):
        time.append(240 - (time_s[j] - time_s[0]).seconds / 60)
    data['time_step'] = time
    
    #產生test_data
    data_n = data.drop_duplicates(subset=['ID'], keep='last')
    data_n = data_n.reset_index(drop=True)
    label = []
    sequential_list = []
    time_step = []
    
    for i in range(len(data_n)):
        PatientID = data_n['ID'][i]
        dialysis_time = data_n['透析開始時間'][i]
        record_time = data_n['紀錄時間'][i]
        filter = ((data['ID'] == PatientID) & (data['透析開始時間'] == dialysis_time) & (data['紀錄時間'] <= record_time))
        sequential_list.append(data[filter][sequential].values[:4].tolist())
        label.append(0)
        time_step.append(data[filter]['time_step'].values[:4].tolist())
    
    traindata = []
    traindata.append(sequential_list)
    traindata.append(label)
    traindata.append(time_step)
    return traindata
#%%
def Predict(traindata):
    batch_size = 8
    dropout_rate = 0.5
    L2_reg = 1e-3
    log_eps = 1e-5
    n_epoch = 20
    n_labels = 2  # binary classification
    visit_size = 128 # size of input embedding
    hidden_size = 128 # size of hidden layer
    gamma = 0.0 # setting for Focal Loss, when it's zero, it's equal to standard cross loss
    use_gpu = False
    layer = 1 # layer of Transformer
    max_len = 50
    total_precision = []
    total_accuracy = []
    total_accuracy = []
    p_out = []
    n_diagnosis_codes=8693

    model_choice = 'TransformerTime' # name of the proposed HiTANet in our paper
    model_file = eval(model_choice)
    options = locals().copy()
    model = model_file(n_diagnosis_codes, batch_size, options)
    model.load_state_dict(torch.load('interface/weights/tran_TransformerTime_hf_sample_L1_wt_1e-4_focal0.00.19'), strict=False)
    
    batch_diagnosis_codes = traindata[0]
    batch_labels = traindata[1]
    batch_time_step = traindata[2]
    batch_diagnosis_codes, batch_time_step = adjust_input(batch_diagnosis_codes, batch_time_step, max_len, n_diagnosis_codes)
    
    lengths = np.array([len(seq) for seq in batch_diagnosis_codes])
    maxlen = np.max(lengths)
    model.eval()
    logit, labels, self_attention = model(batch_diagnosis_codes, batch_time_step, batch_labels, options, maxlen)
    p_out.append(logit)
    del model
    return logit[:,1]
#%%
def predict_idh():
    traindata = Data_Preprocess("interface/data/temp.csv")
    if len(traindata) == 1:
        return [0]
    prediction = Predict(traindata)
    prediction = prediction.detach().numpy()
    # print(prediction)
    return prediction