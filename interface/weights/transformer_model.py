import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import pickle
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, auc, precision_recall_curve
import math

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=500):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.pe = nn.Parameter(pe.unsqueeze(0), requires_grad=False)  # 不讓模型學習它

    def forward(self, x):
        return self.pe[:, :x.size(1), :]
        
# 定義 Transformer 模型
class TransformerModel(nn.Module):
    def __init__(self, input_dim, num_classes, num_heads, num_layers, dim_feedforward, dropout=0.1):
        super(TransformerModel, self).__init__()
        self.embedding = nn.Linear(input_dim, dim_feedforward)
        # self.positional_encoding = nn.Parameter(torch.zeros(1, 500, dim_feedforward))
        self.positional_encoding = PositionalEncoding(dim_feedforward)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=dim_feedforward,
            nhead=num_heads,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True  # Enable batch-first format
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # 增加多頭自注意力機制輸出層
        self.multihead_attn = nn.MultiheadAttention(embed_dim=dim_feedforward, num_heads=num_heads, batch_first=True)
        
        self.fc = nn.Linear(dim_feedforward, num_classes)
    
    def forward(self, x):
        seq_len = x.size(1)
        # x = self.embedding(x) + self.positional_encoding[:, :seq_len, :]
        x = self.embedding(x) + self.positional_encoding(x)
        x = self.transformer_encoder(x)

        attn_output, _ = self.multihead_attn(x, x, x)
        x = attn_output.mean(dim=1) 
        
        out = self.fc(x)
        return out