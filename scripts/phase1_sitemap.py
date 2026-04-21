#!/usr/bin/env python3
"""
Phase 1: 重新產生 sitemap.xml
----------------------------
新 sitemap 包含：
  1. 首頁 /
  2. 8 個服務頁 /pages/*.html
  3. /blog/（部落格首頁）
  4. 所有 blog/articles/*.html（排除 auto-* 實驗生成物等）
  
排除：
  - 根目錄 60 個已轉址檔案
  - 轉址資料夾（22 個服務 + 517 個文章）
"""
import re
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).resolve().parent.parent
TODAY = datetime.now().strftime("%Y-%m-%d")

urls = []

def add(loc, priority="0.5", changefreq="monthly", lastmod=None):
    entry = {"loc": loc, "priority": priority, "changefreq": changefreq}
    if lastmod:
        entry["lastmod"] = lastmod
    urls.append(entry)

# 1. 首頁
add("https://www.bqfox.com/", "1.0", "weekly", TODAY)

# 2. 8 個服務頁
service_pages = sorted((REPO / "pages").glob("*.html"))
for f in service_pages:
    add(f"https://www.bqfox.com/pages/{f.name}", "0.9", "monthly", TODAY)

# 3. 部落格首頁
add("https://www.bqfox.com/blog/", "0.8", "weekly", TODAY)

# 4. 部落格文章（排除壞掉的 / 自動生成的低品質文章）
blog_articles = sorted((REPO / "blog/articles").glob("*.html"))
EXCLUDE = set()  # 可在此排除壞檔
for f in blog_articles:
    if f.stem in EXCLUDE:
        continue
    # 檢查文章是否有 title（排除壞檔）
    html = f.read_text(encoding='utf-8', errors='ignore')
    m = re.search(r'<title>(.*?)</title>', html, re.I|re.S)
    if not m or '{title}' in m.group(1) or '{st}' in html[:3000]:
        print(f"⚠️  Excluding {f.name} (broken title/template)")
        continue
    add(f"https://www.bqfox.com/blog/articles/{f.name}", "0.6", "monthly")

# Write XML
lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    lines.append('  <url>')
    lines.append(f'    <loc>{u["loc"]}</loc>')
    if "lastmod" in u:
        lines.append(f'    <lastmod>{u["lastmod"]}</lastmod>')
    lines.append(f'    <changefreq>{u["changefreq"]}</changefreq>')
    lines.append(f'    <priority>{u["priority"]}</priority>')
    lines.append('  </url>')
lines.append('</urlset>')

sm_path = REPO / "sitemap.xml"
sm_path.write_text('\n'.join(lines) + '\n', encoding="utf-8")

print(f"✅ Wrote {len(urls)} URLs to sitemap.xml")
print(f"   - 1 homepage")
print(f"   - {len(service_pages)} service pages")
print(f"   - 1 blog index")
print(f"   - {len(urls) - 2 - len(service_pages)} blog articles")
