#!/usr/bin/env python3
"""
方向 D 清理腳本：刪除所有中文命名資料夾
在 bqfox-site repo 根目錄執行：python cleanup_chinese_folders.py
"""
import os
import shutil
import sys

# 確認當前目錄是 bqfox-site
if not os.path.exists('_worker.js'):
    print("❌ 錯誤：這個腳本要在 bqfox-site 資料夾裡執行")
    print("   請先 cd 到 bqfox-site 資料夾，再執行此腳本")
    sys.exit(1)

deleted_folders = []
deleted_bytes = 0

# 1. 刪除 /f/ 底下所有中文資料夾
if os.path.isdir('f'):
    for sub in os.listdir('f'):
        path = os.path.join('f', sub)
        if os.path.isdir(path):
            # 統計檔案大小
            for root, _, files in os.walk(path):
                for f in files:
                    deleted_bytes += os.path.getsize(os.path.join(root, f))
            shutil.rmtree(path)
            deleted_folders.append(path)
    # 如果 /f/ 變空，整個刪掉
    if not os.listdir('f'):
        os.rmdir('f')
        deleted_folders.append('f')

# 2. 刪除整個 /首頁/ 資料夾
if os.path.isdir('首頁'):
    for root, _, files in os.walk('首頁'):
        for f in files:
            deleted_bytes += os.path.getsize(os.path.join(root, f))
    shutil.rmtree('首頁')
    deleted_folders.append('首頁')

# 3. 根目錄中文類別資料夾
ROOT_CN = [
    '三七五租約解約','道路用地買賣','重劃地買賣','祭祀公業','公同共有',
    '公同共有處理','日據繼承','未辦繼承','未辦繼承處理','地籍清理',
    '浮覆地復權','持份土地買賣','持份土地買賣、租賃','各種超困難案件處理',
    '各種持份土地買賣','容積移轉代辦','兩岸三地繼承','我們的陣容-1',
    '關於我們','聯絡我們','與我們聯絡',
]
for name in ROOT_CN:
    if os.path.isdir(name):
        for root, _, files in os.walk(name):
            for f in files:
                deleted_bytes += os.path.getsize(os.path.join(root, f))
        shutil.rmtree(name)
        deleted_folders.append(name)

print(f"✅ 刪除 {len(deleted_folders)} 個資料夾")
print(f"   釋放 {deleted_bytes:,} bytes ({deleted_bytes/1024:.1f} KB)")
print(f"")
print(f"接下來請回到 GitHub Desktop，會看到約 540 個 Deleted 變更")
print(f"Commit message: chore(cleanup): remove 539 Chinese redirect folders")
print(f"然後 Push origin")
