#!/usr/bin/env python3
"""Generate the LEGACY_FILE_REDIRECTS block to insert into _worker.js"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Read the Phase 1 summary to get all redirect mappings
summary = json.loads((REPO / "scripts" / "phase1-summary.json").read_text(encoding="utf-8"))
redirects = summary["redirects"]

# Read existing worker
worker_path = REPO / "_worker.js"
worker = worker_path.read_text(encoding="utf-8")

# Build the new redirect map
lines = []
lines.append("// ============================================")
lines.append("// Phase 1: 根目錄重複 HTML → blog/articles/ 或 pages/")
lines.append("// （已同時用 meta-refresh 做 HTML fallback；此處為 server-side 301）")
lines.append("// ============================================")
lines.append("const LEGACY_FILE_REDIRECTS = {")
for r in redirects:
    src = r["src"]
    target = r["target"]
    lines.append(f"  '/{src}': '{target}',")
lines.append("};")
lines.append("")

block = "\n".join(lines)

# Insert block right after EXACT_REDIRECTS (before KEYWORD_RULES comment)
marker = "// ============================================\n// 關鍵字分類規則"
assert marker in worker, "Couldn't find insertion marker in _worker.js"
new_worker = worker.replace(marker, block + "\n" + marker, 1)

# Update getRedirectTarget to check LEGACY_FILE_REDIRECTS after EXACT_REDIRECTS
lookup_old = """  // 1. 精確對應表
  if (EXACT_REDIRECTS[path]) {
    return EXACT_REDIRECTS[path];
  }

  // 2. 文章頁格式：/f/[標題] 或 /首頁/f/[標題]"""
lookup_new = """  // 1. 精確對應表
  if (EXACT_REDIRECTS[path]) {
    return EXACT_REDIRECTS[path];
  }

  // 1.5. 根目錄舊命名 HTML 檔（Phase 1 deduplication）
  if (LEGACY_FILE_REDIRECTS[path]) {
    return LEGACY_FILE_REDIRECTS[path];
  }

  // 2. 文章頁格式：/f/[標題] 或 /首頁/f/[標題]"""

assert lookup_old in new_worker, "Couldn't find getRedirectTarget body"
new_worker = new_worker.replace(lookup_old, lookup_new, 1)

# Update the top-level comment to mention new responsibility
old_comment = """ * 職責：
 *   1. 攔截 GoDaddy 時代的舊 URL（/三七五租約解約、/f/xxx 等）
 *   2. 301 轉址到現有新站的對應頁面（/pages/xxx.html）
 *   3. 其他請求交還給 Cloudflare 的靜態資產系統"""
new_comment = """ * 職責：
 *   1. 攔截 GoDaddy 時代的舊 URL（/三七五租約解約、/f/xxx 等）
 *   2. 攔截根目錄舊命名 HTML 檔（/375-04.html、/an-01.html 等，Phase 1 dedup）
 *   3. 301 轉址到現有新站的對應頁面（/pages/xxx.html、/blog/articles/）
 *   4. 其他請求交還給 Cloudflare 的靜態資產系統"""

new_worker = new_worker.replace(old_comment, new_comment, 1)

worker_path.write_text(new_worker, encoding="utf-8")
print(f"✅ Updated _worker.js")
print(f"   Added LEGACY_FILE_REDIRECTS with {len(redirects)} entries")
print(f"   New size: {len(new_worker):,} chars")
