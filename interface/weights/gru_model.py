# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 16:40:25 2024

@author: iir (ching chieh Tsao)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from math import e

#%% Setting device
device=torch.device("cpu")

#%% GRU function
Dense = torch.nn.Linear
LayerNorm = torch.nn.LayerNorm
class TimeDistributed(nn.Module):
    def __init__(self, module, batch_first):
        super(TimeDistributed, self).__init__()
        self.module = module
        self.batch_first = batch_first

    def forward(self, input_seq):
        assert len(input_seq.size()) > 2

        reshaped_input = input_seq.contiguous().view(-1, input_seq.size(-1))
        output = self.module(reshaped_input)

        if self.batch_first:
            output = output.contiguous().view(input_seq.size(0), -1, output.size(-1))
        else:
            output = output.contiguous().view(-1, input_seq.size(0), output.size(-1))
        return output

def linear_layer(input_size, size, activation=None, use_time_distributed=False, use_bias=True):
    linear = torch.nn.Linear(input_size, size, bias=use_bias).to(device)
    if use_time_distributed:
        linear = TimeDistributed(linear)
    return linear

def apply_gating_layer(x, hidden_layer_size, dropout_rate=None, use_time_distributed=True, activation=None):
    if dropout_rate is not None:
        x = torch.nn.Dropout(dropout_rate).to(device)(x)

    if use_time_distributed:
        activation_layer = TimeDistributed(
            torch.nn.Linear(x.shape[-1], hidden_layer_size)).to(device)(
            x)
        gated_layer = TimeDistributed(
            torch.nn.Linear(x.shape[-1], hidden_layer_size)).to(device)(
            x)
    else:
        activation_layer = torch.nn.Linear(
            x.shape[-1], hidden_layer_size).to(device)(
            x)
        gated_layer = torch.nn.Linear(
            x.shape[-1], hidden_layer_size).to(device)(
            x)

    return torch.mul(activation_layer, gated_layer).to(device), gated_layer

def add_and_norm(x, y):
    tmp = x + y
    tmp = LayerNorm(tmp.shape).to(device)(tmp)
    return tmp

def gated_residual_network(x, hidden_layer_size, output_size=None, dropout_rate=None, use_time_distributed=True, additional_context=None, return_gate=False):
    # Setup skip connection
    if output_size is None:
        output_size = hidden_layer_size
        skip = x
    else:
        linear = Dense(x.shape[-1], output_size).to(device)
        if use_time_distributed:
            linear = TimeDistributed(linear)
        skip = linear(x)

    # Apply feedforward network
    hidden = linear_layer(
        x.shape[-1],
        hidden_layer_size,
        activation=None,
        use_time_distributed=use_time_distributed)(
        x)

    hidden = torch.nn.ELU()(hidden)
    hidden = linear_layer(
        hidden_layer_size,
        hidden_layer_size,
        activation=None,
        use_time_distributed=use_time_distributed)(
        hidden)

    gating_layer, gate = apply_gating_layer(
        hidden,
        output_size,
        dropout_rate=dropout_rate,
        use_time_distributed=use_time_distributed,
        activation=None)

    if return_gate:
        return add_and_norm(skip, gating_layer), gate
    else:
        # print('skip: ', skip.shape)
        # print('gating_layer: ', gating_layer.shape)
        # print('add_and_norm(skip, gating_layer)', add_and_norm(skip, gating_layer).shape)
        return add_and_norm(skip, gating_layer)

def static_combine_and_mask(embedding):
    embedding = embedding.to(device)
    # Add temporal features
    _, num_time, num_static = embedding.shape

    flatten = torch.nn.Flatten()(embedding)

    # Nonlinear transformation with gated residual network.
    mlp_outputs = gated_residual_network(
        flatten,
        hidden_layer_size=5,
        output_size=num_static,
        dropout_rate=0.2,
        use_time_distributed=False,
        additional_context=None)
    sparse_weights = torch.nn.Softmax()(mlp_outputs)
    sparse_weights = torch.unsqueeze(sparse_weights, -1) # (24, 9, 1) 非時序特徵權重

    trans_emb_list = torch.tensor([]).to(device)
    for i in range(num_static):
        e = gated_residual_network(
            embedding[:, :, i:i + 1],
            hidden_layer_size=1,
            dropout_rate=0.2,
            use_time_distributed=False)
        trans_emb_list = torch.cat((trans_emb_list, e), 2)

    transformed_embedding = torch.permute(trans_emb_list, (0, 2, 1))
    combined = torch.mul(sparse_weights, transformed_embedding)
    combined = torch.permute(combined, (0, 2, 1))
    static_vec = torch.sum(combined, 1)

    return combined, sparse_weights
    
record_num = 4
class GRUNet(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, n_layers, drop_prob=0.5):
        super(GRUNet, self).__init__()
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers

        self.gru = nn.GRU(8, hidden_dim, n_layers, batch_first=True, dropout=drop_prob)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
        self.batch_norm = nn.BatchNorm1d(input_dim)
        self.dropout = nn.Dropout(p=0.5)

        self.layer_t = nn.Linear(record_num, hidden_dim)
        self.layer_c = nn.Linear(input_dim, input_dim, bias=False)
        self.layer_adjust = nn.Linear(hidden_dim, hidden_dim)
        self.gru_adjust = nn.GRU(hidden_dim + 4, hidden_dim, n_layers, batch_first=True, dropout=drop_prob)
        self.layer_final = nn.Linear(hidden_dim, 24)
        self.layer_combine = nn.Linear(24, 1)
        self.softmax = nn.Softmax(dim=0)
        self.info_layer = nn.Linear(4, 4*4)
        self.layer_upsample = nn.Linear(8, 8)
        self.prelu = nn.PReLU()
        #self.gru_temp = nn.GRU(batch_size, hidden_dim, n_layers, batch_first=True, dropout=drop_prob)

        self.multihead_attn = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=4, batch_first=True, dropout=0.5)

        self.final_gru = nn.GRU(hidden_dim, hidden_dim, n_layers, batch_first=True, dropout=drop_prob)


    def forward(self, x, h, c, arpha_h, final_h, t, l, info):
        decay_t = 1 / torch.log(e + t)
        decay_t = self.sigmoid(decay_t)

        # unreliablility-aware attention
        out = self.batch_norm(torch.permute(x, (0, 2, 1)))
        out = torch.permute(out, (0, 2, 1))
        out = self.layer_upsample(out)

        decay_t = torch.unsqueeze(decay_t, 2)
        x_deep, h_deep = self.gru(out * decay_t, h) #左T-GRU


        #print(arpha_h.shape)
        #print(arpha.shape)

        #print(decay_t.shape)

        arpha_deep, arpha_h_deep = self.gru(decay_t * c, arpha_h) # 右T-GRU

        #print(c.shape)
        symptom_attention = x_deep * arpha_deep
        # symptom_attention = x_deep + 0.1 * arpha_deep

        x_adjust = self.relu(self.layer_adjust(symptom_attention))

        # 將non-sequential由(24, 9)變為(24, 4, 9)與x_adjust(24, 4, 256)接在一起過最後的GRU

        info = info.unsqueeze(1)
        info = torch.cat((info, info, info, info), 1)
        static_encoder, static_weights = static_combine_and_mask(info)
  
                # 非時序性
        out, h_out = self.gru_adjust(torch.cat((x_adjust, static_encoder), 2), final_h)
        #out, h_out = self.gru_adjust(x_adjust, final_h)
        out = self.dropout(out)


        # Combine all the features
        out = self.layer_final(out[:,-1])
        f = self.sigmoid(self.layer_combine(out)) # 36->1

        return f, h_deep, arpha_h_deep, h_out

    def init_hidden(self, batch_size):
        weight = next(self.parameters()).data
        hidden = weight.new(self.n_layers, batch_size, self.hidden_dim).zero_().to(device)
        return hidden