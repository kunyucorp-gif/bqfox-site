#!/usr/bin/env python3
"""
建立 meta-refresh 301 轉址資料夾（static fallback for _worker.js）。

目標：當 _worker.js 運作正常時，worker 先攔截；此目錄為 worker 掛掉時的靜態
fallback。對應表必須與 _worker.js 的 EXACT_REDIRECTS 保持一致。
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# 與 _worker.js EXACT_REDIRECTS 同步
REDIRECTS = [
    ("三七五租約解約",       "/pages/tenancy-375.html"),
    ("道路用地買賣",         "/pages/road-land.html"),
    ("祭祀公業",             "/pages/ancestral-land.html"),
    ("公同共有處理",         "/pages/joint-ownership.html"),
    ("公同共有",             "/pages/joint-ownership.html"),
    ("容積移轉代辦",         "/pages/floor-area-ratio.html"),
    ("持份土地買賣、租賃",   "/pages/co-ownership.html"),
    ("持份土地買賣",         "/pages/co-ownership.html"),
    ("各種持份土地買賣",     "/pages/co-ownership.html"),
    ("重劃地買賣",           "/pages/rezoning-land.html"),
    ("兩岸三地繼承",         "/pages/cross-strait-inheritance.html"),
    ("日據繼承",             "/pages/cross-strait-inheritance.html"),
    ("浮覆地復權",           "/pages/road-land.html"),
    ("未辦繼承",             "/blog/index.html"),
    ("未辦繼承處理",         "/blog/index.html"),
    ("地籍清理",             "/blog/index.html"),
    ("各種超困難案件處理",   "/index.html#services"),
    ("與我們聯絡",           "/index.html#contact"),
    ("聯絡我們",             "/index.html#contact"),
    ("關於我們",             "/index.html#about"),
    ("我們的陣容-1",         "/index.html#about"),
    ("首頁",                 "/"),
]

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url={TARGET}">
<link rel="canonical" href="https://www.bqfox.com{TARGET}">
<title>頁面已搬遷 | 寶璣建設</title>
<script>window.location.replace("{TARGET}");</script>
</head>
<body><p>此頁面已搬遷至 <a href="{TARGET}">{TARGET}</a></p></body>
</html>
"""

# Sanity checks
names = [r[0] for r in REDIRECTS]
assert len(names) == len(set(names)), f"Duplicate folder names: {names}"
assert len(REDIRECTS) == 22, f"Expected 22, got {len(REDIRECTS)}"

# Verify every target (strip #fragment, handle "/" → index.html)
missing = []
for _, target in REDIRECTS:
    path_part = target.split("#", 1)[0]
    fs_path = REPO / "index.html" if path_part == "/" else REPO / path_part.lstrip("/")
    if not fs_path.exists():
        missing.append(target)
if missing:
    raise SystemExit(f"⚠️  Target files missing: {set(missing)}")

# Write
for folder, target in REDIRECTS:
    dir_path = REPO / folder
    dir_path.mkdir(parents=True, exist_ok=True)
    (dir_path / "index.html").write_text(
        TEMPLATE.replace("{TARGET}", target), encoding="utf-8"
    )

print(f"✅ Wrote {len(REDIRECTS)} redirect folders (idempotent)")
for folder, target in REDIRECTS:
    print(f"  /{folder}/ → {target}")
