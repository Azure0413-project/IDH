import numpy as np
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import torch
import copy

def pad_time(seq_time_step, options):
    lengths = np.array([len(seq) for seq in seq_time_step])
    maxlen = np.max(lengths)
    for k in range(len(seq_time_step)):
        while len(seq_time_step[k]) < maxlen:
            seq_time_step[k].append(0)

    return seq_time_step

def pad_matrix_new(seq_diagnosis_codes, seq_labels, options):
    lengths = np.array([len(seq) for seq in seq_diagnosis_codes])
    n_samples = len(seq_diagnosis_codes)
    n_diagnosis_codes = options['n_diagnosis_codes']
    maxlen = np.max(lengths)
    lengths_code = []
    for seq in seq_diagnosis_codes:
        for code_set in seq:
            lengths_code.append(len(code_set))
    lengths_code = np.array(lengths_code)
    maxcode = np.max(lengths_code)

    batch_diagnosis_codes = np.zeros((n_samples, maxlen, maxcode), dtype=np.int64) - 1#+ options['n_diagnosis_codes']
    batch_mask = np.zeros((n_samples, maxlen), dtype=np.float32)
    batch_mask_code = np.zeros((n_samples, maxlen, maxcode), dtype=np.float32)
    batch_mask_final = np.zeros((n_samples, maxlen), dtype=np.float32)

    for bid, seq in enumerate(seq_diagnosis_codes):
        for pid, subseq in enumerate(seq):
            for tid, code in enumerate(subseq):
                batch_diagnosis_codes[bid, pid, tid] = code
                batch_mask_code[bid, pid, tid] = 1


    for i in range(n_samples):
        batch_mask[i, 0:lengths[i]-1] = 1
        max_visit = lengths[i] - 1
        batch_mask_final[i, max_visit] = 1


    batch_labels = np.array(seq_labels, dtype=np.int64)

    return batch_diagnosis_codes, batch_labels, batch_mask, batch_mask_final, batch_mask_code


def calculate_cost_tran(model, data, options, max_len, loss_function=F.cross_entropy, weight=torch.tensor([1.0, 1.0])):
    model.eval()
    batch_size = options['batch_size']
    n_batches = int(np.ceil(float(len(data[0])) / float(batch_size)))
    cost_sum = 0.0

    for index in range(n_batches):
        batch_non_time_ori = []
        temperature_ori = []
        batch_diagnosis_codes = data[0][batch_size * index: batch_size * (index + 1)]
        batch_time_step = data[3][batch_size * index: batch_size * (index + 1)]
        for i in range(batch_size):
            if((index * batch_size) + i < len(data[2])):
                batch_non_time_ori.append(data[2][(index * batch_size) + i])
                temperature_ori.append(data[4][(index * batch_size) + i])
        batch_non_time = torch.FloatTensor(batch_non_time_ori)
        temperature = torch.FloatTensor(temperature_ori)
        batch_diagnosis_codes, batch_time_step = adjust_input(batch_diagnosis_codes, batch_time_step, max_len, options['n_diagnosis_codes'])
        batch_labels = data[1][batch_size * index: batch_size * (index + 1)]
        lengths = np.array([len(seq) for seq in batch_diagnosis_codes])
        maxlen = np.max(lengths)
        logit, labels, self_attention = model(batch_diagnosis_codes, batch_time_step, batch_labels, options, maxlen)
        #print(logit)
        #print(labels)
        loss = F.cross_entropy(logit,labels,weight)
        cost_sum += loss.cpu().data.numpy()
    model.train()
    return cost_sum / n_batches


def adjust_input(batch_diagnosis_codes, batch_time_step, max_len, n_diagnosis_codes):
    batch_time_step = copy.deepcopy(batch_time_step)
    batch_diagnosis_codes = copy.deepcopy(batch_diagnosis_codes)
    for ind in range(len(batch_diagnosis_codes)):
        if len(batch_diagnosis_codes[ind]) > max_len:
            batch_diagnosis_codes[ind] = batch_diagnosis_codes[ind][-(max_len):]
            batch_time_step[ind] = batch_time_step[ind][-(max_len):]
        batch_time_step[ind].append(0)
        batch_diagnosis_codes[ind].append([-1])
    return batch_diagnosis_codes, batch_time_step
