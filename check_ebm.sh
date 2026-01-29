#!/bin/bash
# EBM 功能整合自動檢查腳本
# Ubuntu 可以運行，使用方法：bash check_ebm.sh

cd /home/IDH

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 EBM 功能整合檢查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 計數器
total_checks=0
passed_checks=0

# 檢查 1: Model 檔案
total_checks=$((total_checks + 1))
echo "【檢查 1/8】Model 權重檔案..."
if [ -f "interface/weights/TN_EBM_Rename.joblib" ]; then
    size=$(ls -lh interface/weights/TN_EBM_Rename.joblib | awk '{print $5}')
    echo "  ✅ Model 檔案存在 ($size)"
    passed_checks=$((passed_checks + 1))
else
    echo "  ❌ Model 檔案不存在"
    echo "     路徑：interface/weights/TN_EBM_Rename.joblib"
    echo "     請上傳 Model 檔案到此位置"
fi
echo ""

# 檢查 2: EBM.py 檔案是否存在
total_checks=$((total_checks + 1))
echo "【檢查 2/8】EBM.py 檔案是否存在..."
if [ -f "interface/model/EBM.py" ]; then
    echo "  ✅ EBM.py 檔案存在"
    passed_checks=$((passed_checks + 1))
else
    echo "  ❌ EBM.py 檔案不存在"
    echo "     路徑：interface/model/EBM.py"
    echo "     請建立此檔案並加入所需函數"
fi
echo ""

# 檢查 3: EBM.py 是否包含必要的函數
total_checks=$((total_checks + 1))
echo "【檢查 3/8】EBM.py 包含必要函數..."
if [ -f "interface/model/EBM.py" ]; then
    # 檢查三個關鍵函數
    has_check_dialysis=0
    has_calculate_idh=0
    has_prepare_features=0
    has_predict_ebm=0
    
    if grep -q "def check_dialysis_has_idh" interface/model/EBM.py; then
        has_check_dialysis=1
    fi
    if grep -q "def calculate_idh_count_with_dual_mode" interface/model/EBM.py; then
        has_calculate_idh=1
    fi
    if grep -q "def prepare_ebm_features_v2" interface/model/EBM.py; then
        has_prepare_features=1
    fi
    if grep -q "def predict_idh_ebm" interface/model/EBM.py; then
        has_predict_ebm=1
    fi
    
    missing_count=0
    if [ $has_check_dialysis -eq 0 ]; then
        echo "  ⚠️  缺少：check_dialysis_has_idh()"
        missing_count=$((missing_count + 1))
    fi
    if [ $has_calculate_idh -eq 0 ]; then
        echo "  ⚠️  缺少：calculate_idh_count_with_dual_mode()"
        missing_count=$((missing_count + 1))
    fi
    if [ $has_prepare_features -eq 0 ]; then
        echo "  ⚠️  缺少：prepare_ebm_features_v2()"
        missing_count=$((missing_count + 1))
    fi
    if [ $has_predict_ebm -eq 0 ]; then
        echo "  ⚠️  缺少：predict_idh_ebm()"
        missing_count=$((missing_count + 1))
    fi
    
    if [ $missing_count -eq 0 ]; then
        echo "  ✅ 所有必要函數都存在 (4/4)"
        passed_checks=$((passed_checks + 1))
    else
        echo "  ❌ 缺少 $missing_count 個函數"
        echo "     請參考 EBM_DEPLOYMENT_GUIDE.md 補充完整程式碼"
    fi
else
    echo "  ❌ EBM.py 檔案不存在，無法檢查函數"
fi
echo ""

# 檢查 4: views.py 是否有 EBM 預測區塊
total_checks=$((total_checks + 1))
echo "【檢查 4/8】views.py 整合 EBM 預測邏輯..."
if grep -q "EBM 預測區塊開始" interface/views.py; then
    line_num=$(grep -n "EBM 預測區塊開始" interface/views.py | cut -d: -f1)
    echo "  ✅ EBM 預測邏輯已整合 (Line $line_num)"
    
    # 額外檢查關鍵元素
    has_first_record=0
    has_ebm_warning=0
    has_ebm_prob=0
    
    if grep -q "first_record = Record.objects.filter" interface/views.py; then
        has_first_record=1
    fi
    if grep -q "patient\['ebm_warning'\]" interface/views.py; then
        has_ebm_warning=1
    fi
    if grep -q "patient\['ebm_prob'\]" interface/views.py; then
        has_ebm_prob=1
    fi
    
    if [ $has_first_record -eq 1 ] && [ $has_ebm_warning -eq 1 ] && [ $has_ebm_prob -eq 1 ]; then
        echo "  ✅ 包含所有關鍵元素"
        passed_checks=$((passed_checks + 1))
    else
        echo "  ⚠️  預測區塊不完整"
        [ $has_first_record -eq 0 ] && echo "     缺少：first_record 查詢"
        [ $has_ebm_warning -eq 0 ] && echo "     缺少：patient['ebm_warning']"
        [ $has_ebm_prob -eq 0 ] && echo "     缺少：patient['ebm_prob']"
    fi
else
    echo "  ❌ 缺少 EBM 預測邏輯"
    echo "     請在 interface/views.py 的 get_patients() 函數中新增"
    echo "     搜尋關鍵字：#0326 random code"
fi
echo ""

# 檢查 5: index.html 警告圖標
total_checks=$((total_checks + 1))
echo "【檢查 5/8】index.html 新增警告圖標..."
if grep -q "patient.ebm_warning" interface/templates/index.html; then
    line_num=$(grep -n "patient.ebm_warning" interface/templates/index.html | head -1 | cut -d: -f1)
    echo "  ✅ 警告圖標已新增 (Line $line_num)"
    
    # 檢查是否有完整的 img 標籤
    if grep -q "ebm-warning-icon" interface/templates/index.html; then
        echo "  ✅ 包含 CSS class: ebm-warning-icon"
        passed_checks=$((passed_checks + 1))
    else
        echo "  ⚠️  缺少 CSS class: ebm-warning-icon"
    fi
else
    echo "  ❌ 缺少警告圖標"
    echo "     請在 interface/templates/index.html 中新增"
    echo "     搜尋關鍵字：patient.first_click and patient.random_code"
fi
echo ""

# 檢查 6: index.css 樣式
total_checks=$((total_checks + 1))
echo "【檢查 6/8】index.css 新增 CSS 樣式..."
if grep -q "ebm-warning-icon" static/css/index.css; then
    line_num=$(grep -n "ebm-warning-icon" static/css/index.css | head -1 | cut -d: -f1)
    echo "  ✅ CSS 樣式已新增 (Line $line_num)"
    
    # 檢查樣式是否包含必要屬性
    has_position=0
    has_top=0
    has_right=0
    
    if grep -A 8 "ebm-warning-icon" static/css/index.css | grep -q "position.*absolute"; then
        has_position=1
    fi
    if grep -A 8 "ebm-warning-icon" static/css/index.css | grep -q "top.*5px"; then
        has_top=1
    fi
    if grep -A 8 "ebm-warning-icon" static/css/index.css | grep -q "right.*5px"; then
        has_right=1
    fi
    
    if [ $has_position -eq 1 ] && [ $has_top -eq 1 ] && [ $has_right -eq 1 ]; then
        echo "  ✅ CSS 屬性完整"
        passed_checks=$((passed_checks + 1))
    else
        echo "  ⚠️  CSS 屬性不完整"
        [ $has_position -eq 0 ] && echo "     缺少：position: absolute"
        [ $has_top -eq 0 ] && echo "     缺少：top: 5px"
        [ $has_right -eq 0 ] && echo "     缺少：right: 5px"
    fi
else
    echo "  ❌ 缺少 CSS 樣式"
    echo "     請在 static/css/index.css 末尾新增 .ebm-warning-icon"
fi
echo ""

# 檢查 7: joblib 套件
total_checks=$((total_checks + 1))
echo "【檢查 7/8】joblib 套件安裝..."
if python3 -c "import joblib" 2>/dev/null; then
    version=$(python3 -c "import joblib; print(joblib.__version__)" 2>/dev/null)
    echo "  ✅ joblib 已安裝 (版本: $version)"
    passed_checks=$((passed_checks + 1))
else
    echo "  ❌ joblib 未安裝"
    echo "     請執行：pip install joblib"
fi
echo ""

# 檢查 8: Python 模組導入
total_checks=$((total_checks + 1))
echo "【檢查 8/8】測試 EBM 模組導入..."
if python3 -c "from interface.model.EBM import predict_idh_ebm; print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "  ✅ EBM 模組導入成功"
    passed_checks=$((passed_checks + 1))
else
    echo "  ❌ 模組導入失敗"
    echo "     可能原因："
    echo "     1. EBM.py 檔案不存在或不完整"
    echo "     2. 程式碼有語法錯誤"
    echo "     3. joblib 未安裝"
    echo ""
    echo "     測試導入："
    python3 -c "from interface.model.EBM import predict_idh_ebm" 2>&1 | head -5 | sed 's/^/     /'
fi
echo ""

# 總結
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $passed_checks -eq $total_checks ]; then
    echo "🎉 全部通過！($passed_checks/$total_checks)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "✅ EBM 功能已成功整合"
    echo ""
    echo "📝 下一步："
    echo "   1. 重啟 Django server: python manage.py runserver"
    echo "   2. 觀察 Console 日誌，尋找 [EBM] 開頭的訊息"
    echo "   3. 前端應顯示驚嘆號警告（如有符合條件的病人）"
    echo ""
    exit 0
else
    echo "⚠️  檢查結果：$passed_checks/$total_checks 通過"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "❌ 請修正上方顯示的問題"
    echo ""
    echo "📖 參考文件："
    echo "   - 完整指南：cat EBM_DEPLOYMENT_GUIDE.md"
    echo "   - 快速開始：cat README_FIRST.txt"
    echo ""
    echo "修正後重新執行：bash check_ebm.sh"
    echo ""
    exit 1
fi
