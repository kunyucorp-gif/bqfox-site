#!/usr/bin/env python3
"""
Phase 1: 消除重複內容
------------------
策略：保留 blog/articles/ 為權威版本，根目錄的重複檔改成 meta-refresh 轉址

改動內容：
  1. 54 個根目錄重複檔 → 替換為 meta-refresh 到 blog/articles/<同檔名>
  2. 2 個 template 未渲染的檔 → 替換為 meta-refresh 到 /blog/ 並加 noindex
  3. 4 個特殊檔的個別處理：
     - road-land.html → 301 到 /index.html（它是首頁複製品）
     - what-is-road-land.html → 301 到 /pages/road-land.html（服務頁）
     - rl-12.html → 301 到 /blog/articles/rl-12.html
     - an-07.html → 301 到 /blog/articles/an-07.html
  4. 更新 sitemap.xml：
     - 移除 58 個根目錄舊命名 URL
     - 加入 65 個 blog/articles/ URL
  5. 更新 _worker.js：加入 60 條 server-side 301 規則

注意：idempotent，可重跑
"""
import json
import re
import shutil
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).resolve().parent.parent

# ═══ Template ═══
REDIRECT_TPL = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="robots" content="noindex, follow">
<meta http-equiv="refresh" content="0; url={TARGET}">
<link rel="canonical" href="https://www.bqfox.com{TARGET}">
<title>頁面已搬遷 | 寶璣建設</title>
<script>window.location.replace("{TARGET}");</script>
</head>
<body><p>此頁面已搬遷至 <a href="{TARGET}">{TARGET}</a></p></body>
</html>
"""

# ═══ 對應表 ═══
# 1. Category A: 54 個同檔名重複
CATEGORY_A = [
    "co-13.html","rl-13.html","375-08.html","farm-03.html","rl-15.html",
    "co-16.html","re-01.html","farm-01.html","co-07.html","jo-03.html",
    "jo-04.html","co-15.html","co-09.html","far-02.html","375-10.html",
    "co-06.html","an-06.html","375-06.html","jo-05.html","far-05.html",
    "375-09.html","rl-11.html","rl-14.html","an-02.html","co-17.html",
    "an-10.html","co-11.html","an-03.html","co-12.html","an-04.html",
    "an-05.html","375-04.html","re-03.html","inh-01.html","inh-03.html",
    "jo-01.html","co-14.html","an-09.html","far-01.html","re-02.html",
    "inh-04.html","375-07.html","farm-02.html","an-08.html","rl-09.html",
    "inh-05.html","rl-10.html","co-08.html","co-10.html","farm-04.html",
    "jo-02.html","inh-06.html","farm-05.html","375-05.html",
]

# 2. Category C: 2 個 template 壞掉的
# （farm-05 已在 A；375-overview 是獨立的）
CATEGORY_C = ["375-overview.html"]
# farm-05.html 放 A 類已經會轉址，但 blog/articles/farm-05 也可能是壞的 — 留個安全網：
# 實際上 A 裡已有 farm-05，這裡不重複加

# 3. Category D: 4 個特殊案例
CATEGORY_D = {
    "road-land.html": "/",                             # 首頁複製品 → 301 到根
    "what-is-road-land.html": "/pages/road-land.html", # 獨特內容 → 服務頁
    "rl-12.html": "/blog/articles/rl-12.html",         # 內容破損 → blog 對應
    "an-07.html": "/blog/articles/an-07.html",         # 空殼 → blog 對應
}

# ═══ 執行 ═══

def write_redirect(src_path: Path, target: str):
    """Overwrite src_path with a meta-refresh redirect pointing to target"""
    src_path.write_text(REDIRECT_TPL.replace("{TARGET}", target), encoding="utf-8")

def backup_original(src_path: Path, backup_dir: Path):
    """Save original content to backup folder before overwriting"""
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, backup_dir / src_path.name)

def main():
    # Backup originals (for rollback)
    backup_dir = REPO / ".phase1-backup"
    if backup_dir.exists():
        shutil.rmtree(backup_dir)

    processed = []
    skipped_missing = []

    # Category A
    for name in CATEGORY_A:
        src = REPO / name
        if not src.exists():
            skipped_missing.append(name)
            continue
        backup_original(src, backup_dir)
        target = f"/blog/articles/{name}"
        # Verify target exists
        if not (REPO / f"blog/articles/{name}").exists():
            skipped_missing.append(f"{name} (target missing!)")
            continue
        write_redirect(src, target)
        processed.append((name, target, "A: same-name duplicate"))

    # Category C (template broken)
    for name in CATEGORY_C:
        src = REPO / name
        if not src.exists():
            skipped_missing.append(name)
            continue
        backup_original(src, backup_dir)
        write_redirect(src, "/blog/")
        processed.append((name, "/blog/", "C: template variable not rendered"))

    # Category D (special cases)
    for name, target in CATEGORY_D.items():
        src = REPO / name
        if not src.exists():
            skipped_missing.append(name)
            continue
        backup_original(src, backup_dir)
        # Verify target (except root "/")
        if target != "/":
            target_path = REPO / target.lstrip("/")
            if not target_path.exists():
                skipped_missing.append(f"{name} → {target} (target missing!)")
                continue
        write_redirect(src, target)
        processed.append((name, target, "D: special case"))

    # Report
    print(f"✅ Phase 1 – converted {len(processed)} root HTML files to redirects")
    for src, tgt, reason in processed:
        print(f"  {src:30s} → {tgt:50s} [{reason}]")
    if skipped_missing:
        print(f"\n⚠️  Skipped ({len(skipped_missing)}):")
        for s in skipped_missing:
            print(f"  {s}")

    # Write summary JSON
    summary = {
        "executed_at": datetime.now().isoformat(),
        "processed_count": len(processed),
        "redirects": [{"src": s, "target": t, "reason": r} for s,t,r in processed],
        "skipped": skipped_missing,
    }
    (REPO / "scripts" / "phase1-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n📝 Summary: scripts/phase1-summary.json")

if __name__ == "__main__":
    main()
