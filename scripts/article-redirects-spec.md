# 寶璣建設：擴大 meta refresh 資料夾到所有 GoDaddy 舊文章 URL

## 背景

上次已經建了 22 個服務類別資料夾。現在要把**所有從 Google Search Console 有流量紀錄的舊文章 URL**（`/f/XXX` 和 `/首頁/f/XXX` 格式）也都做成 meta refresh 資料夾。

預估 517 個資料夾，Linux 檔案系統完全相容（已實測），Git 也能正常追蹤中文路徑。

## 檔案需求

請先找我要 `gsc-urls.json` 這份檔案（裡面是 GSC 匯出的 812 個 URL 含流量）。

如果我沒給，請用下面這個清單做為 input source（把 JSON 內容貼進腳本）。

## 任務

在 repo 根目錄擴充 meta refresh 資料夾，對每個 GSC 有流量的舊文章 URL：
- `/f/XXX` → 建 `XXX/index.html`（注意：不是 `f/XXX/`，是把 `f/` 去掉）

  等等，這裡要精確：實際的舊 URL 是 `https://www.bqfox.com/f/文章標題` 這樣的路徑，
  所以要建的是 `f/文章標題/index.html`，meta refresh 到對應目標。

- `/首頁/f/XXX` → 建 `首頁/f/XXX/index.html`

## 分類邏輯（跟 _worker.js 一致）

每個文章標題依關鍵字分類到目標頁：

```python
KEYWORD_RULES = [
    (['三七五', '375', '減租', '佃農', '耕地租佃'], '/pages/tenancy-375.html'),
    (['容積移轉', '容積率', '送出基地', '接受基地', '容積代金'], '/pages/floor-area-ratio.html'),
    (['公同共有', '派下員'], '/pages/joint-ownership.html'),
    (['祭祀公業', '神明會', '祭田'], '/pages/ancestral-land.html'),
    (['持分', '分別共有', '持份', '應有部分', '鑑界'], '/pages/co-ownership.html'),
    (['重劃', '區段徵收'], '/pages/rezoning-land.html'),
    (['兩岸', '大陸繼承', '日據繼承', '日治', '港澳'], '/pages/cross-strait-inheritance.html'),
    (['道路用地', '既成道路', '計畫道路', '公設保留地', '公共設施保留地',
      '馬路', '巷道', '公告現值', '徵收', '容積獎勵', '私設道路',
      '都市計畫道路', '浮覆地'], '/pages/road-land.html'),
    (['農地', '農舍', '自地自建', '未辦繼承', '逾期繼承'], '/blog/index.html'),
    (['地籍清理', '未保存登記', '地上權', '建築套繪'], '/blog/index.html'),
    (['地價稅', '贈與稅', '遺產稅', '土地稅', '節稅'], '/blog/index.html'),
    (['共有', '土地買賣', '過戶', '蓋房子', '蓋民宿', '建地', '綠地'], '/pages/co-ownership.html'),
]

def classify(title):
    for kws, target in KEYWORD_RULES:
        for kw in kws:
            if kw in title:
                return target
    return '/blog/index.html'  # 無關鍵字命中 → 導到 blog 首頁
```

## HTML Template

每個 index.html 用這個模板（跟之前的 22 個資料夾相同）：

```html
<!DOCTYPE html>
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
```

## 腳本位置

擴充現有的 `scripts/create_redirects.py`，或新建 `scripts/create_article_redirects.py`。

**選擇：建議新建一個 `create_article_redirects.py`**，跟 22 個服務資料夾的腳本分開管理（服務頁規則穩定，文章規則會擴充）。

## 腳本邏輯

```python
import json
import os
from pathlib import Path

# 讀 GSC 資料（使用者會提供 gsc-urls.json 檔案路徑，或把資料 hardcode）
with open('data/gsc-urls.json', 'r', encoding='utf-8') as f:
    urls = json.load(f)

# 收集所有 /f/ 和 /首頁/f/ 路徑
articles = {}  # path -> target

for u in urls:
    path = u['path_decoded'].rstrip('/')
    title = None
    if path.startswith('/首頁/f/'):
        title = path[len('/首頁/f/'):]
    elif path.startswith('/f/'):
        title = path[len('/f/'):]
    
    if title:
        target = classify(title)
        articles[path] = target

# 產生實體資料夾
REPO_ROOT = Path(__file__).parent.parent
TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="https://www.bqfox.com{target}">
<title>頁面已搬遷 | 寶璣建設</title>
<script>window.location.replace("{target}");</script>
</head>
<body><p>此頁面已搬遷至 <a href="{target}">{target}</a></p></body>
</html>
'''

created = 0
skipped = 0

for path, target in articles.items():
    # path 例：/f/三七五減租廢除了嗎？ 或 /首頁/f/道路用地可以圍起來嗎？
    folder = REPO_ROOT / path.lstrip('/')
    folder.mkdir(parents=True, exist_ok=True)
    
    index_file = folder / 'index.html'
    content = TEMPLATE.format(target=target)
    
    if index_file.exists() and index_file.read_text(encoding='utf-8') == content:
        skipped += 1
    else:
        index_file.write_text(content, encoding='utf-8')
        created += 1

print(f"建立/更新: {created}")
print(f"已存在無變化: {skipped}")
print(f"總文章資料夾: {len(articles)}")
```

## 執行

```bash
# 先取得 gsc-urls.json（如果使用者沒給，向他索取）
# 建議放在 data/gsc-urls.json

# 執行腳本
python3 scripts/create_article_redirects.py

# 驗證
git add .
git status --porcelain | wc -l      # 預期 ~517 + 1（腳本） = 518 檔

# 隨機抽查
find f/ -name "index.html" | head -3
cat "f/三七五減租廢除了嗎？/index.html" 2>/dev/null | head -5

# 再跑一次驗證 idempotent
python3 scripts/create_article_redirects.py
git status --porcelain | wc -l      # 應該不變
```

## 驗證事項

1. ✅ 共產生約 517 個資料夾（精確數字以腳本實跑為準）
2. ✅ 每個資料夾都有 `index.html`
3. ✅ 特殊字元（`？` `、` `｜` `《》` 等）處理正常
4. ✅ 長檔名（最長約 150 bytes）正常
5. ✅ 所有 target URL 指向的檔案在 repo 中存在：
   - `/pages/*.html`（8 個服務頁）
   - `/blog/index.html`（部落格首頁）
6. ✅ Idempotent：重跑零 drift

## ⚠️ 重要限制

1. **不要動既有的 22 個服務資料夾** — 那是另一個腳本 `create_redirects.py` 管理
2. **不要動 `_worker.js`** — 保留做為另一層 server-side 301
3. **不要動 `scripts/generate_article.py`** — 那是自動生成新文章的
4. **不要自動 commit、不要自動 push** — 讓我手動確認

## 完成後回報

- 產生了幾個資料夾
- `git status` 輸出（中文路徑可讀版本 `git -c core.quotepath=false status`）
- 隨機抽查一個 `index.html` 的內容
- idempotent 驗證（重跑 `git status` 應無差異）
