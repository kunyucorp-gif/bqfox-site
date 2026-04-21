#!/usr/bin/env python3
"""
Phase 6: Add article-level precise redirects.
將舊的 /f/xxx 和 /首頁/f/xxx URL 對應到新 Batch 1 的文章。
"""
import re
from pathlib import Path
import json

REPO = Path(__file__).resolve().parent.parent

# 每篇新文章對應的舊 URL 標題（從 GSC 真實資料看）
# key = 新文章 slug（不含 .html）
# value = list of 舊文章標題（無 /f/ 前綴）
ARTICLE_MAP = {
    'co-rental-fenbie': [
        '分別共有可以出租嗎？——土地專家的淺白解說',
        '分別共有可以出租嗎？',
    ],
    'co-vs-joint-ownership-distinction': [
        '如何知道土地是共同共有還是分別共有？',
        '「公同共有」與「分別共有」的差別？',
        '「公同共有」與「分別共有」的差別',
    ],
    'co-ownership-gift-guide': [
        '分別共有可以贈與嗎？',
        '分別共有土地贈與',
    ],
    'co-ownership-boundary-survey': [
        '持分土地可以鑑界嗎？',
    ],
    'co-ownership-pricing': [
        '持分土地要怎麼定價？影響價格的關鍵因素一次看',
    ],
    'co-ownership-building-house': [
        '持分土地能蓋房子嗎？法規限制與申請程序解析',
    ],
    'co-ownership-buy-sell-guide': [
        '持分土地可以買賣嗎？注意事項與交易流程全解析',
    ],
    'co-ownership-partition-guide': [
        '【超詳解懶人包】一張圖搞懂共有土地分割！專家教你避開法律陷阱',
    ],
    'co-ownership-inheritance': [
        '持分土地怎麼繼承？避免爭議的-3-個關鍵重點',
        '持分土地怎麼繼承？避免爭議的 3 個關鍵重點',
    ],
}

# Build flat list of (old_path, new_path) pairs
precise_redirects = {}
for slug, old_titles in ARTICLE_MAP.items():
    new_url = f'/blog/articles/{slug}.html'
    for old_title in old_titles:
        precise_redirects[f'/f/{old_title}'] = new_url
        precise_redirects[f'/首頁/f/{old_title}'] = new_url

print(f"📋 新增精確轉址：{len(precise_redirects)} 條")
for k, v in list(precise_redirects.items())[:6]:
    print(f"  {k[:50]:<52s} → {v}")
print("  ...")

# Read existing worker
worker_path = REPO / '_worker.js'
worker = worker_path.read_text(encoding='utf-8')

# Build the JS map
js_lines = [
    '// ============================================',
    '// Phase 6 (Batch 1)：精確文章 URL → 新文章',
    '// 舊的 /f/xxx 標題，精確轉到對應的新文章（優先於關鍵字規則）',
    '// ============================================',
    'const ARTICLE_PRECISE_REDIRECTS = {',
]
for old, new in precise_redirects.items():
    # Escape single quotes in old path
    old_escaped = old.replace("'", "\\'")
    js_lines.append(f"  '{old_escaped}': '{new}',")
js_lines.append('};')
js_lines.append('')

new_block = '\n'.join(js_lines)

# Check if already injected
if 'ARTICLE_PRECISE_REDIRECTS' in worker:
    # Replace existing block
    worker = re.sub(
        r'// ={10,}\n// Phase 6.*?\n\};\n',
        new_block,
        worker, flags=re.S
    )
    print("\n♻️  更新既有的 ARTICLE_PRECISE_REDIRECTS block")
else:
    # Insert before KEYWORD_RULES
    marker = '// ============================================\n// 關鍵字分類規則'
    assert marker in worker
    worker = worker.replace(marker, new_block + '\n' + marker)
    print("\n➕  新增 ARTICLE_PRECISE_REDIRECTS block")

# Now update getRedirectTarget to check ARTICLE_PRECISE_REDIRECTS first for /f/ paths
lookup_old = """  if (articleTitle) {
    // 依關鍵字判定
    for (const rule of KEYWORD_RULES) {"""

lookup_new = """  if (articleTitle) {
    // 先檢查精確文章對應（Phase 6）
    if (ARTICLE_PRECISE_REDIRECTS[path]) {
      return ARTICLE_PRECISE_REDIRECTS[path];
    }
    // 依關鍵字判定
    for (const rule of KEYWORD_RULES) {"""

if lookup_old in worker and 'ARTICLE_PRECISE_REDIRECTS[path]' not in worker:
    worker = worker.replace(lookup_old, lookup_new)
    print("✅ 更新 getRedirectTarget 邏輯")

worker_path.write_text(worker, encoding='utf-8')
print(f"\n✅ _worker.js 更新完成（{len(worker):,} chars）")

# Validate JS syntax
import subprocess
result = subprocess.run(['node', '-e', f'''
const content = require("fs").readFileSync("_worker.js", "utf-8");
try {{
  new Function(content.replace(/export default/g, "const _ = "));
  console.log("✅ JS syntax valid");
}} catch(e) {{
  console.error("❌ Syntax error:", e.message);
  process.exit(1);
}}
'''], capture_output=True, text=True)
print(result.stdout + result.stderr)
