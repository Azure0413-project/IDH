# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 16:40:25 2024

@author: iir (ching chieh Tsao)
"""

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from math import e
from interface.weights.gru_model import *
import warnings
import os
import datetime
from interface.weights.transformer_model import TransformerModel   # 0814 added
warnings.filterwarnings("ignore")

def getNowDatee():
    now = datetime.datetime.now()
    year = '{:02d}'.format(now.year)
    month = '{:02d}'.format(now.month)
    day = '{:02d}'.format(now.day)
    hour = '{:02d}'.format(now.hour)
    minute = '{:02d}'.format(now.minute)
    day_month_year = '{}-{}-{} {}:{}'.format(year, month, day, hour, minute)
    # print('day_month_year: ' + day_month_year)
    return day_month_year
#%%
def check_condition(data_point):
    """
    Checks if a data point meets the specified conditions.

    Args:
        data_point: A list representing a single data point.

    Returns:
        True if the data point meets all conditions, False otherwise.
    """
    return (
        (data_point[2] >= 80) & (data_point[2] <= 1000) and 
        (data_point[4] >= 30) & (data_point[4] <= 150) and 
        (data_point[5] >= 5) & (data_point[5] <= 40) and 
        (data_point[3] <= 7) and 
        (data_point[6] >= 60) & (data_point[6] <= 400) and 
        (data_point[7] >= 34) & (data_point[7] <= 39) and 
        (data_point[0] >= 60) & (data_point[0] <= 250) & (data_point[0] >= data_point[1]) and 
        (data_point[1] >= 25) & (data_point[1] <= 150) & (data_point[1] <= data_point[0])
    )

def Data_Preprocess(file_name):
    try:
        data = pd.read_csv(file_name, encoding='utf-8_sig', engine='python')
        # data = pd.read_csv(file_name, encoding='utf-8', engine='python')
        temp = ['透析開始時間', '紀錄時間']
        for i in temp:
            data[i] = pd.to_datetime(data[i])
        
        sequential = ['血壓(收縮)', '血壓(舒張)', '透析液流速(ml/min)', '脫水速率', '脈搏', '呼吸', '血流速(ml/min)', '透析液溫度(℃)']
        for i in sequential:
            data[i] = pd.to_numeric(data[i],errors='coerce')
        data = data.fillna(-1)
        
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
        info_list = []
        
        for i in range(len(data_n)):
            PatientID = data_n['ID'][i]
            dialysis_time = data_n['透析開始時間'][i]
            record_time = data_n['紀錄時間'][i]
            filter = ((data['ID'] == PatientID) & (data['透析開始時間'] == dialysis_time) & (data['紀錄時間'] <= record_time))

            filtered_data = data[filter][sequential].values[:4]

            # Filter data based on the specified conditions
            filtered_data = [data_point for data_point in filtered_data 
                             if check_condition(data_point)]

            if filtered_data:
                sequential_list.append(filtered_data)
                label.append(0)
                info_list.append([0]*28)
                time_step.append(data[filter]['time_step'].values[:4].tolist())

        traindata = []
        
        traindata.append(sequential_list)
        traindata.append(label)
        traindata.append(info_list)
        traindata.append(time_step)

        return traindata
    
    except Exception as error:
            noww = getNowDatee()
            with open('data_list_sucess.txt', 'a') as file:
                file.write(f"Date: {noww}")
                file.write(str(error))
                file.write("\n")
                # json.dump(data_list, json_file, indent=4)  # Write the data to a file in JSON 
            print("save sucesssfully")

# 0814 added
def Data_Preprocess_for_Transformer(file_name):
    """
    [Final Version] Replicates the feature engineering from the source notebook.
    It calculates 3 _Var features based on 'Start_SBP' and 'Start_DBP'.
    """
    try:
        data = pd.read_csv(file_name, encoding='utf-8_sig', engine='python')
        
        # Define the base 8 features, using 'Start_SBP' and 'Start_DBP' as per the notebook
        base_sequential_features = [
            'Start_SBP', 'Start_DBP', '透析液流速(ml/min)', '脫水速率', '脈搏', '呼吸', 
            '血流速(ml/min)', '透析液溫度(℃)'
        ]
        
        for col in base_sequential_features:
            data[col] = pd.to_numeric(data[col], errors='coerce')

        # --- Replicate Feature Engineering ---
        data['透析開始時間'] = pd.to_datetime(data['透析開始時間'], errors='coerce')
        data['紀錄時間'] = pd.to_datetime(data['紀錄時間'], errors='coerce')
        data = data.sort_values(by=['ID', '透析開始時間', '紀錄時間']).reset_index(drop=True)
        
        grouped = data.groupby(['ID', '透析開始時間'])
        def cumulative_variance(x):
            valid_x = x.dropna()
            return valid_x.expanding().var()

        data['脈搏_Var'] = grouped['脈搏'].apply(lambda group: cumulative_variance(group)).reset_index(level=[0, 1], drop=True)
        data['Start_SBP_Var'] = grouped['Start_SBP'].apply(lambda group: cumulative_variance(group)).reset_index(level=[0, 1], drop=True)
        data['Start_DBP_Var'] = grouped['Start_DBP'].apply(lambda group: cumulative_variance(group)).reset_index(level=[0, 1], drop=True)
        
        data = data.fillna(0.0)

        # Calculate time_step
        time_s_groups = data.groupby(['ID', '透析開始時間'])['紀錄時間']
        time_deltas = time_s_groups.transform(lambda x: (x - x.iloc[0]).dt.total_seconds() / 60)
        data['time_step'] = 240 - time_deltas
        
        # Define the final 11 features to be used
        final_sequential_features = base_sequential_features + ['脈搏_Var', 'Start_SBP_Var', 'Start_DBP_Var']
        
        data_n = data.drop_duplicates(subset=['ID'], keep='last').reset_index(drop=True)
        sequential_list = []
        time_step_list = []
        
        for i in range(len(data_n)):
            PatientID = data_n['ID'][i]
            dialysis_time = data_n['透析開始時間'][i]
            
            patient_records = data[(data['ID'] == PatientID) & (data['透析開始時間'] == dialysis_time)]
            
            filtered_data_seq = patient_records[final_sequential_features].values.tolist()
            filtered_data_time = patient_records['time_step'].values.tolist()

            sequential_list.append(filtered_data_seq)
            time_step_list.append(filtered_data_time)
            
        return sequential_list, time_step_list

    except Exception as error:
        noww = getNowDatee()
        with open('error_log.txt', 'a') as file:
            file.write(f"Date: {noww} - Transformer Preprocess Error: {error}\n")
        print(f"Error during Transformer data preprocessing: {error}")
        import traceback
        traceback.print_exc()
        return None, None
            
# def adjust_input(input_data, zero_list, record_num = 4):
#     for i in range(len(input_data)):
#         while(len(input_data[i]) < record_num):
#             input_data[i].append(zero_list)
#     return np.array(input_data)

# the old adjust input
# def adjust_input(input_data, zero_list, record_num=4):
#     for i in range(len(input_data)):
#         while len(input_data[i]) < record_num:
#             input_data[i].append(zero_list)
#     # Convert to float64 (or another numeric type)
#     return np.array(input_data, dtype=np.float64)

# 0814
# new adjust_input
def adjust_input(input_data, padding_value, max_len=4):
    processed_data = []
    for seq in input_data:
        # 截斷或填充序列
        if len(seq) > max_len:
            seq = seq[-max_len:]
        while len(seq) < max_len:
            seq.insert(0, padding_value) # 向前填充
        processed_data.append(seq)
    return np.array(processed_data, dtype=np.float64)

def zero_norm(data):
    mean, std, var = torch.mean(data), torch.std(data), torch.var(data)
    data = (data-mean)/std
    return data

def cal_x_len(data):
    l = []
    for i in data:
        l.append(len(i))
    return np.array(l)
#%%

def Predict(model_path, test_x, test_u, test_t, test_y, test_l, test_info, device=torch.device("cpu")):
    model = GRUNet(input_dim = 8, hidden_dim=256, output_dim = 1, n_layers = 1, drop_prob=0.5)
    model.to(device)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    
    preds = []

    inp = torch.from_numpy(test_x)
    u_inp = torch.from_numpy(1+test_u)
    t_inp = torch.from_numpy(test_t)
    labs = torch.from_numpy(test_y)
    l_inp = torch.from_numpy(test_l)
    info_inp = torch.from_numpy(test_info)

    h = model.init_hidden(inp.shape[0])
    arpha_h = model.init_hidden(inp.shape[0])
    middle_h = model.init_hidden(inp.shape[0])
    final_h = model.init_hidden(inp.shape[0]) #h

    out, h, arpha_h, final_h = model(inp.to(device).float(), h, u_inp.to(device).float(), arpha_h, final_h, t_inp.to(device).float(), l_inp.to(device).float(), info_inp.to(device).float())
    preds.append((out.cpu().detach().numpy()).reshape(-1))
#     print("results: ", preds[0])
    results = [round(num, 4) for num in preds[0]]
    return results

# 0814 added

def Predict_Transformer(model_path, test_x, test_t, device=torch.device("cpu")):
    """
    [無標準化測試版] 
    職責：初始化模型，載入訓練成果，直接吃下未經標準化的原始數據，然後給出預測分數。
    """
    input_dim, num_classes, num_heads, num_layers, dim_feedforward = 12, 2, 4, 2, 128
    model = TransformerModel(input_dim, num_classes, num_heads, num_layers, dim_feedforward)
    model.to(device)

    try:
        model.load_state_dict(torch.load(model_path, map_location=device))
        print(">>> Model weights loaded successfully.")
    except Exception as e:
        print(f">>> FATAL: Error loading model weights: {e}")
        return [0.0] * len(test_x)

    model.eval()
    
    # 將時間特徵拼接到生理特徵後面，組成12個特徵的最終輸入
    test_t = np.expand_dims(test_t, axis=-1)
    combined_inp = np.concatenate((test_x, test_t), axis=-1)
    
    print(">>> [NO SCALING] Shape of final input tensor:", combined_inp.shape)
    print(">>> [NO SCALING] Sample of final input data (first patient, last timestep):\n", combined_inp[0][-1])
    
    inp = torch.from_numpy(combined_inp).to(device).float()

    with torch.no_grad():
        out = model(inp)
        probabilities = F.softmax(out, dim=1)
        preds = probabilities[:, 1].cpu().numpy()

    results = [round(float(num), 4) for num in preds]
    print(f"len of final prediction:{len(results)}\n")
    print(">>> [NO SCALING] Final predictions:", results)
    return results



#%%

# old predict_idh
# def predict_idh():
#     traindata = Data_Preprocess('interface/data/temp.csv')
#     if traindata is None:
#         print("Error: DataPreprocess returned None")
#         return

#     # sequential variable
#     zero_list = [-1] * 8

#     batch_size = 1
#     # non-sequential
#     # info = np.array(traindata[3], zero_list)
#     # info = adjust_input(traindata[3], zero_list)

#     # sequential's length (for last embedding)
#     seq_length = cal_x_len(traindata[0])
    
#     sequential = adjust_input(traindata[0], zero_list)
#     # time step
#     zero_list = 480
#     time_step = adjust_input(traindata[3], zero_list)
#     time_step = np.array(zero_norm(torch.from_numpy(time_step))) # zero_mean
#     for i in range(len(time_step)):
#         for j in range(len(time_step[0])):
#             if time_step[i][j] < -2.712:
#                 time_step[i][j] = -0.7452
#     # unreliable
#     similarity_score = np.zeros(sequential.shape)
#     # label
#     y = np.array(traindata[1])
#     y = np.expand_dims(y, axis=1)
    
#     prediction = Predict(model_path='interface/weights/balance_train_good', test_x=sequential, test_u=similarity_score, test_t=time_step, test_y=y, test_l=seq_length, test_info=time_step)
#     return prediction

# 0814 added new predict_idh & cancel old version
def predict_idh():
    """
    [無標準化測試版] 
    這個版本移除了 Min-Max 標準化步驟，直接將原始數據餵給模型。
    """
    print("--- Starting IDH prediction with Transformer model [NO SCALING TEST] ---")
    
    # 步驟 1: 處理資料
    sequential_list, time_step_list = Data_Preprocess_for_Transformer('interface/data/temp.csv')
    
    if sequential_list is None:
        print(">>> Error: Data Preprocessing failed.")
        try:
            data = pd.read_csv('interface/data/temp.csv', encoding='utf-8_sig', engine='python')
            return [0.0] * data['ID'].nunique()
        except:
            return [0.0] * 33

    # 步驟 2: 填充 (Padding)
    seq_padding_value = [0.0] * 11 
    sequential_padded = adjust_input(sequential_list, seq_padding_value, max_len=4)
    
    time_padding_value = 0.0
    time_step_padded = adjust_input(time_step_list, time_padding_value, max_len=4)

    # 步驟 3: [已移除] 標準化步驟被跳過了
    # scaled_sequential = manual_min_max_scaler(...)
    # scaled_time_step = manual_min_max_scaler(...)

    # 步驟 4: 呼叫預測器，但傳入的是未經標準化的原始數據
    prediction = Predict_Transformer(
        model_path='interface/weights/best_transformer_model_newvar.pth',
        test_x=sequential_padded,  # <--- 直接傳入填充後的原始數據
        test_t=time_step_padded   # <--- 直接傳入填充後的原始數據
    )
    
    print("--- IDH prediction finished [NO SCALING TEST] ---")
    return prediction