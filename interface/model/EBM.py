# interface/model/EBM.py

def check_dialysis_has_idh(dialysis_id, use_database_flag=True):
    """
    判斷某次透析是否有發生 IDH
    
    兩種模式：
    1. use_database_flag=True: 使用資料庫中的 is_idh 標記
    2. use_database_flag=False: 使用邏輯判斷（Nadir90/100 規則）
    
    Args:
        dialysis_id: Dialysis 的 d_id
        use_database_flag: 是否優先使用資料庫標記
    
    Returns:
        bool: True 表示該次透析有 IDH, False 表示沒有
    """
    from interface.models import Dialysis, Record
    
    dialysis = Dialysis.objects.get(d_id=dialysis_id)
    
    # 取得該次透析的所有 Record（按時間排序）
    records = Record.objects.filter(
        d_id=dialysis
    ).order_by('record_time')
    
    if records.count() == 0:
        return False  # 沒有紀錄，無法判斷
    
    # ========== 模式 1: 使用資料庫標記 ==========
    if use_database_flag:
        # 只要有一個 record 的 is_idh=True，就認為這次透析有 IDH
        if records.filter(is_idh=True).exists():
            return True
    
    # ========== 模式 2: 邏輯判斷（改寫自 Nadir90/100 邏輯） ==========
    # 改寫你提供的程式碼邏輯
    
    # 取得 Start_SBP（透析開始時的收縮壓）
    start_sbp = float(dialysis.start_SBP) if dialysis.start_SBP else None
    
    if start_sbp is None or start_sbp < 50:
        # 如果沒有 Start_SBP 或數值異常，無法判斷
        return False
    
    # 取得所有有效的 SBP 讀數（>= 50 且不為 0）
    valid_sbp_records = []
    for record in records:
        sbp = float(record.SBP)
        if sbp >= 50 and sbp != 0:
            valid_sbp_records.append(sbp)
    
    if len(valid_sbp_records) == 0:
        return False  # 沒有有效的 SBP 讀數
    
    # 根據 Start_SBP 決定閾值
    # 如果 Start_SBP < 160: 使用 90 作為閾值
    # 如果 Start_SBP >= 160: 使用 100 作為閾值
    if start_sbp < 160:
        threshold = 90
    else:
        threshold = 100
    
    # 檢查是否有任何一個有效讀數低於閾值
    for sbp_value in valid_sbp_records:
        if sbp_value < threshold:
            return True  # 找到 IDH
    
    return False  # 沒有找到 IDH


def calculate_idh_count_with_dual_mode(patient_id, current_start_time, days=7, use_database_flag=True):
    """
    計算該病人在過去 N 天內發生 IDH 的次數（不含當天）
    
    支援雙重模式：
    1. use_database_flag=True: 優先使用資料庫標記，失敗時用邏輯判斷
    2. use_database_flag=False: 只用邏輯判斷
    
    Args:
        patient_id: 病人ID
        current_start_time: 當前透析開始時間
        days: 要回溯的天數 (7 或 28)
        use_database_flag: 是否使用資料庫標記
    
    Returns:
        int: IDH 發生次數
    """
    from interface.models import Dialysis, Record
    from datetime import timedelta
    
    # 計算時間範圍（不含當天）
    end_date = current_start_time.date()
    start_date = end_date - timedelta(days=days)
    
    # 透過 FK 查詢該病人在此時間範圍內的所有透析
    past_dialysis_list = Dialysis.objects.filter(
        p_id=patient_id,
        start_time__date__gte=start_date,
        start_time__date__lt=end_date
    )
    
    idh_count = 0
    
    for past_dialysis in past_dialysis_list:
        # 使用上面定義的函數判斷
        has_idh = check_dialysis_has_idh(
            past_dialysis.d_id, 
            use_database_flag=use_database_flag
        )
        
        if has_idh:
            idh_count += 1
    
    return idh_count


def prepare_ebm_features_v2(dialysis_id, use_database_flag=True):
    """
    準備 EBM Model 所需的 16 個特徵（支援雙重模式）
    
    Args:
        dialysis_id: Dialysis 的 d_id
        use_database_flag: 是否使用資料庫標記判斷 IDH
    
    Returns:
        dict: 包含 16 個特徵的字典
    """
    from interface.models import Dialysis, Record, Patient
    
    # 取得核心資料
    dialysis = Dialysis.objects.get(d_id=dialysis_id)
    patient = dialysis.p_id
    
    # 取得最新 record
    latest_record = Record.objects.filter(
        d_id=dialysis
    ).order_by('-record_time').first()
    
    # 處理 Record 可能不存在的情況
    if latest_record:
        pulse_value = int(latest_record.pulse)
        breath_value = float(latest_record.breath)
        dialyse_temp_value = float(latest_record.dialyse_temperature)
    else:
        pulse_value = 80
        breath_value = 18.0
        dialyse_temp_value = float(dialysis.start_temperature) if dialysis.start_temperature else 36.5
    
    # 計算 UF_BW_Perc
    before_weight = float(dialysis.before_weight)
    uf_bw_perc_value = (
        float(dialysis.expect_dehydration) / before_weight 
        if before_weight > 0 else 0.0
    )
    
    # 計算歷史 IDH（使用雙重模式）
    idh_7d = calculate_idh_count_with_dual_mode(
        patient.p_id, 
        dialysis.start_time, 
        days=7,
        use_database_flag=use_database_flag
    )
    
    idh_28d = calculate_idh_count_with_dual_mode(
        patient.p_id, 
        dialysis.start_time, 
        days=28,
        use_database_flag=use_database_flag
    )
    
    # 組合特徵
    features = {
        '性別': 1 if patient.gender == '男' else 0,
        '年齡': int(dialysis.age),
        'IDH_N_7D': idh_7d,
        'IDH_N_28D': idh_28d,
        'Start_SBP': float(dialysis.start_SBP) if dialysis.start_SBP else 0.0,
        'Start_DBP': int(dialysis.start_DBP),
        '脈搏': pulse_value,
        '呼吸': breath_value,
        '開始體溫': float(dialysis.start_temperature) if dialysis.start_temperature else 36.5,
        '透析前體重(kg)': before_weight,
        '理想體重(kg)': float(dialysis.ideal_weight),
        '目標脫水量(L)': float(dialysis.expect_dehydration),
        'UF_BW_Perc': uf_bw_perc_value,
        '開始血液流速': float(dialysis.start_blood_speed) if dialysis.start_blood_speed else 0.0,
        '開始透析液流速': float(dialysis.start_flow_speed) if dialysis.start_flow_speed else 0.0,
        '透析液溫度(℃)': dialyse_temp_value,
    }
    
    return features


def predict_idh_ebm(dialysis_id, use_database_flag=False):
    """
    使用 EBM Model 預測 IDH 風險
    
    Args:
        dialysis_id: Dialysis 的 d_id
        use_database_flag: 是否使用資料庫標記（預設 False，使用邏輯判斷）
    
    Returns:
        float: IDH 預測機率 (0-1)
    """
    import joblib
    from decimal import Decimal
    
    try:
        # 1. 載入 EBM model
        model = joblib.load('/home/nckuh-nephro/Desktop/IDH_interface/interface/weights/TN_EBM_Rename.joblib')
        
        # 2. 準備特徵
        features = prepare_ebm_features_v2(dialysis_id, use_database_flag)
        
        # 3. 確保特徵順序正確
        feature_names = [
            '性別', '年齡', 'IDH_N_7D', 'IDH_N_28D', 'Start_SBP', 'Start_DBP',
            '脈搏', '呼吸', '開始體溫', '透析前體重(kg)', '理想體重(kg)',
            '目標脫水量(L)', 'UF_BW_Perc', '開始血液流速', '開始透析液流速',
            '透析液溫度(℃)'
        ]
        
        # 檢查 model 是否有 feature_names_in_
        if hasattr(model, 'feature_names_in_'):
            feature_names = model.feature_names_in_
        
        # 組成特徵向量
        feature_vector = [features[name] for name in feature_names]
        
        # 4. 預測
        prediction_proba = model.predict_proba([feature_vector])[0][1]
        
        print(f"[EBM] Dialysis {dialysis_id}: probability = {prediction_proba:.4f}")
        print(f"[EBM] Features: IDH_7D={features['IDH_N_7D']}, IDH_28D={features['IDH_N_28D']}")
        
        return float(prediction_proba)
        
    except Exception as e:
        print(f"[EBM] Error predicting for dialysis {dialysis_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0.0