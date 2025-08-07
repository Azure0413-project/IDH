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

        self.layer_t = nn.Linear(4, hidden_dim)
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
        return f, h_deep, arpha_h_deep, h_out, out

    def init_hidden(self, batch_size):
        weight = next(self.parameters()).data
        hidden = weight.new(self.n_layers, batch_size, self.hidden_dim).zero_().to(device)
        return hidden