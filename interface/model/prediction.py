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
warnings.filterwarnings("ignore")
#%%
def Data_Preprocess(file_name):
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
        sequential_list.append(data[filter][sequential].values[:4].tolist())
        label.append(0)
        info_list.append([0]*28)
        time_step.append(data[filter]['time_step'].values[:4].tolist())
    
    traindata = []
    traindata.append(sequential_list)
    traindata.append(label)
    traindata.append(info_list)
    traindata.append(time_step)
    return traindata

def adjust_input(input_data, zero_list, record_num = 4):
    for i in range(len(input_data)):
        while(len(input_data[i]) < record_num):
            input_data[i].append(zero_list)
    return np.array(input_data)

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
    final_h = model.init_hidden(inp.shape[0])

    out, h, arpha_h, final_h, latent_embd = model(inp.to(device).float(), h, u_inp.to(device).float(), arpha_h, final_h, t_inp.to(device).float(), l_inp.to(device).float(), info_inp.to(device).float())
    preds.append((out.cpu().detach().numpy()).reshape(-1))
#     print("results: ", preds[0])
    results = [round(num, 4) for num in preds[0]]
    return results
#%%

def predict_idh():
    traindata = Data_Preprocess('interface/data/temp.csv')
    batch_size = 1
    # non-sequential
    info = np.array(traindata[2])
    # sequential's length (for last embedding)
    seq_length = cal_x_len(traindata[0])
    # sequential variable
    zero_list = [-1] * 8
    sequential = adjust_input(traindata[0], zero_list)
    # time step
    zero_list = 480
    time_step = adjust_input(traindata[3], zero_list)
    time_step = np.array(zero_norm(torch.from_numpy(time_step))) # zero_mean
    for i in range(len(time_step)):
        for j in range(len(time_step[0])):
            if time_step[i][j] < -2.712:
                time_step[i][j] = -0.7452
    # unreliable
    similarity_score = np.zeros(sequential.shape)
    # label
    y = np.array(traindata[1])
    y = np.expand_dims(y, axis=1)
    
    prediction = Predict(model_path='interface/weights/IDH_NCKUH_model_weight_202402210204_0_117', test_x=sequential, test_u=similarity_score, test_t=time_step, test_y=y, test_l=seq_length, test_info=info)
    return prediction