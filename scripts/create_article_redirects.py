#!/usr/bin/env python3
"""
建立 GSC 有流量的舊文章 URL 的 meta-refresh 轉址資料夾。

來源：data/gsc-urls.json（GSC 匯出）
處理：/f/XXX 與 /首頁/f/XXX 兩種格式
分類：依標題關鍵字映射到目標頁，規則與 _worker.js KEYWORD_RULES 同步

注意：這腳本專管文章轉址，服務類別資料夾由 scripts/create_redirects.py 負責。
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "gsc-urls.json"

# 與 _worker.js KEYWORD_RULES 同步（順序重要：特異性高的先）
KEYWORD_RULES = [
    (["三七五", "375", "減租", "佃農", "耕地租佃"], "/pages/tenancy-375.html"),
    (["容積移轉", "容積率", "送出基地", "接受基地", "容積代金"], "/pages/floor-area-ratio.html"),
    (["公同共有", "派下員"], "/pages/joint-ownership.html"),
    (["祭祀公業", "神明會", "祭田"], "/pages/ancestral-land.html"),
    (["持分", "分別共有", "持份", "應有部分", "鑑界"], "/pages/co-ownership.html"),
    (["重劃", "區段徵收"], "/pages/rezoning-land.html"),
    (["兩岸", "大陸繼承", "日據繼承", "日治", "港澳"], "/pages/cross-strait-inheritance.html"),
    (["道路用地", "既成道路", "計畫道路", "公設保留地", "公共設施保留地",
      "馬路", "巷道", "公告現值", "徵收", "容積獎勵", "私設道路",
      "都市計畫道路", "浮覆地"], "/pages/road-land.html"),
    (["農地", "農舍", "自地自建", "未辦繼承", "逾期繼承"], "/blog/index.html"),
    (["地籍清理", "未保存登記", "地上權", "建築套繪"], "/blog/index.html"),
    (["地價稅", "贈與稅", "遺產稅", "土地稅", "節稅"], "/blog/index.html"),
    (["共有", "土地買賣", "過戶", "蓋房子", "蓋民宿", "建地", "綠地"], "/pages/co-ownership.html"),
]
FALLBACK = "/blog/index.html"

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


def classify(title: str) -> str:
    for kws, target in KEYWORD_RULES:
        if any(kw in title for kw in kws):
            return target
    return FALLBACK


def extract_article_paths(urls: list) -> dict:
    """Return {path: (title, target)} for /f/ and /首頁/f/ entries, deduped."""
    out = {}
    for entry in urls:
        path = entry["path_decoded"].rstrip("/")
        if path.startswith("/首頁/f/"):
            title = path[len("/首頁/f/"):]
        elif path.startswith("/f/"):
            title = path[len("/f/"):]
        else:
            continue
        if "/" in title:
            # Safety: title must not embed path separators
            print(f"⚠️  Skipping path with nested slash: {path!r}", file=sys.stderr)
            continue
        if not title:
            continue
        out[path] = (title, classify(title))
    return out


def main() -> int:
    if not DATA.exists():
        sys.exit(f"❌ Missing input: {DATA}")

    with DATA.open(encoding="utf-8") as f:
        urls = json.load(f)

    articles = extract_article_paths(urls)
    print(f"📊 Found {len(articles)} unique article paths in GSC export")

    # Verify target files exist in repo
    unique_targets = set(t for _, t in articles.values())
    for t in sorted(unique_targets):
        if not (REPO / t.lstrip("/")).exists():
            sys.exit(f"❌ Target missing in repo: {t}")
    print(f"✅ All {len(unique_targets)} target files exist in repo")

    created, updated, skipped = 0, 0, 0
    target_counts = {}

    for path, (title, target) in articles.items():
        folder = REPO / path.lstrip("/")
        folder.mkdir(parents=True, exist_ok=True)
        index_file = folder / "index.html"
        content = TEMPLATE.replace("{TARGET}", target)

        if index_file.exists():
            if index_file.read_text(encoding="utf-8") == content:
                skipped += 1
            else:
                index_file.write_text(content, encoding="utf-8")
                updated += 1
        else:
            index_file.write_text(content, encoding="utf-8")
            created += 1

        target_counts[target] = target_counts.get(target, 0) + 1

    print()
    print(f"✍️  Created: {created}")
    print(f"🔁 Updated: {updated}")
    print(f"💤 Skipped (identical): {skipped}")
    print(f"📦 Total folders: {len(articles)}")
    print()
    print("🎯 Target distribution:")
    for t, n in sorted(target_counts.items(), key=lambda kv: -kv[1]):
        print(f"   {n:>4}  → {t}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
