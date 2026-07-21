import os
import glob
import json
import django

# ==========================================
# 1. 初始化 Django 環境設定
# ==========================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idh.settings') # 請確認你的主設定目錄名稱（通常為 idh）
django.setup()

# 匯入專案腳本中已有的轉換與儲存函式
from scripts.fetch_API import convertCSV  # 請依據你實際檔名調整引用
from scripts.load_data import saveData    # 請依據你實際檔名調整引用

def parse_txt_and_import():
    """
    讀取根目錄下所有 YYYY-MM.txt 備份檔，
    解析 JSON 後重新匯入資料庫。
    """
    # 搜尋當前目錄下所有符合 YYYY-MM.txt 格式的檔案
    txt_files = sorted(glob.glob("20[0-9][0-9]-[0-1][0-9].txt"))
    
    if not txt_files:
        print("❌ 未找到任何 YYYY-MM.txt 檔案，請確認路徑！")
        return

    print(f"🔍 找到 {len(txt_files)} 個歷史紀錄文字檔: {txt_files}\n")

    for file_path in txt_files:
        print(f"==========================================")
        print(f"📂 正在處理歷史檔案: {file_path}")
        print(f"==========================================")
        
        all_data_list = []
        
        # 以唯讀模式開啟檔案，確保完全不影響原始 txt 內容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                # 避開 Date: 開頭的標記行以及空行
                if not line or line.startswith("Date:"):
                    continue
                
                try:
                    # 去除 html meta 標籤並解析 JSON
                    clean_line = line.strip('<meta charset="UTF-8" />')
                    json_obj = json.loads(clean_line)
                    
                    if 'data_list' in json_obj and json_obj['data_list']:
                        all_data_list.extend(json_obj['data_list'])
                except json.JSONDecodeError:
                    # 跳過非標準 JSON 的雜訊行
                    continue
                except Exception as e:
                    print(f"⚠️ 解析單行資料時發生錯誤: {e}")

        if not all_data_list:
            print(f"⚠️ 檔案 {file_path} 內無有效的 data_list 資料，跳過。")
            continue

        print(f"✅ 成功從 {file_path} 解析出 {len(all_data_list)} 筆 raw data 紀錄。")
        
        # 1. 將解析出來的數據轉換為 interface/data/temp.csv
        print("🔄 正在生成中間檔 interface/data/temp.csv ...")
        convertCSV(all_data_list)
        
        # 2. 注意：需確認你的 splitCSV() 是否需要在 saveData 前執行
        # 如果你的 load_data 需要 splitCSV 切成 patient.csv / dialysis.csv / record.csv
        # 請確保在 saveData 前呼叫 splitCSV()
        try:
            from scripts.DBbuilder import splitCSV
            print("✂️ 正在切分 CSV 為 patient.csv, dialysis.csv, record.csv ...")
            splitCSV()
        except ImportError:
            print("ℹ️ 未檢測到 splitCSV，直接執行 saveData...")

        # 3. 寫入 DB (根據 `.exists()` 補齊缺失資料)
        print("💾 正在將數據同步補回 db.sqlite3 ...")
        saveData()
        print(f"✨ {file_path} 處理完成！\n")

    print("🎉 所有 txt 歷史數據已成功補回資料庫！")

if __name__ == "__main__":
    parse_txt_and_import()