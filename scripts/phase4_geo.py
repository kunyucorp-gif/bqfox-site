#!/usr/bin/env python3
"""
Phase 4: GEO（生成式引擎優化）
================================
讓 ChatGPT / Perplexity / Gemini / Claude 等 AI 引擎引用本站內容。

做法（不動現有內容，純加法）：
  1. 為 8 個服務頁抽取 FAQ → 生成 FAQPage JSON-LD schema
  2. 升級 Service schema（加 areaServed、dateModified、hasOfferCatalog）
  3. 加 Article/WebPage schema + dateModified
  4. 加入「AI 摘要」(summary) 段落作為 description
  5. （另外生）llms.txt：AI 引擎專用 sitemap
  6. （另外生）更新 robots.txt：明確允許 AI 爬蟲

Idempotent：用 <!-- PHASE4_SCHEMA --> 標記判斷
"""
import json
import re
from datetime import datetime
from html import unescape
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TODAY = datetime.now().strftime("%Y-%m-%d")
ISO_NOW = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

# ════════════════════════════════════════════════════════════
# 頁面設定（URL path → 服務資訊）
# ════════════════════════════════════════════════════════════
PAGES = {
    "pages/road-land.html": {
        "service_name": "道路用地買賣代辦",
        "service_desc": "協助全台地主出售道路用地、既成道路、公共設施保留地，建商直接收購。",
        "audience": "道路用地所有人、繼承取得道路地地主",
        "price_range": "依公告現值 30%-140% 不等，視區域、持分、地上物而定",
    },
    "pages/floor-area-ratio.html": {
        "service_name": "容積移轉代辦",
        "service_desc": "公共設施保留地所有人辦理容積移轉，換取合理補償。",
        "audience": "公設保留地、道路用地所有人",
        "price_range": "代辦費依容積量體議價",
    },
    "pages/rezoning-land.html": {
        "service_name": "重劃地買賣",
        "service_desc": "市地重劃區、區段徵收區土地買賣仲介。",
        "audience": "重劃區土地所有人",
        "price_range": "依土地實際價值議價",
    },
    "pages/tenancy-375.html": {
        "service_name": "三七五租約解約代辦",
        "service_desc": "依《耕地三七五減租條例》協助地主合法終止租約、處理佃農補償。",
        "audience": "受三七五租約束縛的耕地地主",
        "price_range": "依耕地面積與佃農補償議價",
    },
    "pages/co-ownership.html": {
        "service_name": "持份土地買賣代辦",
        "service_desc": "分別共有不動產買賣，依土地法第 34-1 條處分。",
        "audience": "分別共有土地所有人",
        "price_range": "依持分比例與土地區位議價",
    },
    "pages/joint-ownership.html": {
        "service_name": "公同共有處理",
        "service_desc": "繼承未分割、派下員意見不一的公同共有土地整合。",
        "audience": "公同共有土地所有人、繼承人",
        "price_range": "代辦費依案件複雜度議價",
    },
    "pages/ancestral-land.html": {
        "service_name": "祭祀公業土地處理",
        "service_desc": "派下員認定、祭祀公業法人登記、土地分割、標售。",
        "audience": "祭祀公業派下員、神明會成員",
        "price_range": "代辦費依土地筆數與派下員人數議價",
    },
    "pages/cross-strait-inheritance.html": {
        "service_name": "兩岸三地繼承",
        "service_desc": "兩岸、港澳、日據時期等跨境或跨時代不動產繼承。",
        "audience": "海外繼承人、日據時期舊慣繼承關係人",
        "price_range": "代辦費依繼承人數與跨境複雜度議價",
    },
}

ORG = {
    "@type": ["RealEstateAgent", "LocalBusiness"],
    "@id": "https://www.bqfox.com/#org",
    "name": "寶璣建設有限公司",
    "url": "https://www.bqfox.com",
    "logo": "https://www.bqfox.com/assets/logo.svg",
    "telephone": "02-2274-6789",
    "taxID": "94157953",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "南雅南路二段144巷73號",
        "addressLocality": "板橋區",
        "addressRegion": "新北市",
        "postalCode": "220",
        "addressCountry": "TW",
    },
}


# ════════════════════════════════════════════════════════════
# FAQ 抽取
# ════════════════════════════════════════════════════════════

def extract_faqs(html: str):
    """從 <details><summary>Q</summary><p>A</p></details> 抓出 FAQ"""
    faqs = []
    pattern = re.compile(
        r'<details[^>]*class=["\']faq-item["\'][^>]*>\s*'
        r'<summary>(.*?)</summary>\s*'
        r'<p>(.*?)</p>\s*'
        r'</details>',
        re.I | re.S
    )
    for m in pattern.finditer(html):
        q = unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()
        a = unescape(re.sub(r'<[^>]+>', '', m.group(2))).strip()
        if q and a:
            faqs.append({"question": q, "answer": a})
    return faqs


def build_schemas(page_path: str, meta: dict, html: str):
    """產出 FAQ + Service + WebPage + BreadcrumbList schemas"""
    faqs = extract_faqs(html)
    url = f"https://www.bqfox.com/{page_path}"

    # 抓 title / description
    title_m = re.search(r'<title>(.*?)</title>', html, re.I | re.S)
    desc_m = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.I | re.S)
    title = title_m.group(1).strip() if title_m else meta["service_name"]
    description = desc_m.group(1).strip() if desc_m else meta["service_desc"]

    schemas = []

    # 1. FAQPage
    if faqs:
        schemas.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "@id": f"{url}#faq",
            "mainEntity": [{
                "@type": "Question",
                "name": f["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f["answer"],
                },
            } for f in faqs],
        })

    # 2. Service (升級版)
    schemas.append({
        "@context": "https://schema.org",
        "@type": "Service",
        "@id": f"{url}#service",
        "name": meta["service_name"],
        "description": meta["service_desc"],
        "serviceType": meta["service_name"],
        "provider": {"@id": "https://www.bqfox.com/#org"},
        "areaServed": {
            "@type": "Country",
            "name": "Taiwan",
        },
        "audience": {
            "@type": "Audience",
            "audienceType": meta["audience"],
        },
        "offers": {
            "@type": "Offer",
            "priceCurrency": "TWD",
            "priceSpecification": {
                "@type": "PriceSpecification",
                "priceCurrency": "TWD",
                "description": meta["price_range"],
            },
            "availability": "https://schema.org/InStock",
        },
    })

    # 3. WebPage + dateModified
    schemas.append({
        "@context": "https://schema.org",
        "@type": "WebPage",
        "@id": f"{url}#webpage",
        "url": url,
        "name": title,
        "description": description,
        "inLanguage": "zh-TW",
        "isPartOf": {"@id": "https://www.bqfox.com/#website"},
        "about": {"@id": "https://www.bqfox.com/#org"},
        "dateModified": ISO_NOW,
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "首頁", "item": "https://www.bqfox.com/"},
                {"@type": "ListItem", "position": 2, "name": "營業項目",
                 "item": "https://www.bqfox.com/#services"},
                {"@type": "ListItem", "position": 3, "name": meta["service_name"], "item": url},
            ],
        },
    })

    return schemas, faqs


def inject_schemas(html: str, schemas: list, faqs: list) -> str:
    """把新的 schemas 插進 </head>，並加 marker"""
    # 清掉舊的 phase4 schema block（若有）
    html = re.sub(
        r'<!-- PHASE4_SCHEMA_START -->.*?<!-- PHASE4_SCHEMA_END -->\s*',
        '', html, flags=re.S
    )

    # Build new block
    block = ["<!-- PHASE4_SCHEMA_START -->"]
    for s in schemas:
        block.append(
            f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False, separators=(",", ":"))}</script>'
        )
    # AI 摘要：顯示在頁面（用 <meta> 加 summary + itemscope）
    if faqs:
        block.append(f'<meta name="ai-summary" content="本頁涵蓋 {len(faqs)} 個常見問題：{"、".join([f["question"][:20] for f in faqs[:3]])} 等。">')
    block.append(f'<meta name="last-modified" content="{TODAY}">')
    block.append("<!-- PHASE4_SCHEMA_END -->")

    # Insert before </head>
    html = html.replace('</head>', '\n'.join(block) + '\n</head>', 1)
    return html


# ════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════

def main():
    print("Phase 4: GEO 優化\n" + "═" * 70)
    faq_counts = {}

    for rel, meta in PAGES.items():
        f = REPO / rel
        if not f.exists():
            print(f"⚠️  missing: {rel}")
            continue

        html = f.read_text(encoding="utf-8")
        schemas, faqs = build_schemas(rel, meta, html)
        new_html = inject_schemas(html, schemas, faqs)
        f.write_text(new_html, encoding="utf-8")
        faq_counts[rel] = len(faqs)
        print(f"  {rel:45s} FAQ={len(faqs)}  schemas={len(schemas)}")

    print()
    print(f"總 FAQ 題目：{sum(faq_counts.values())}")

if __name__ == "__main__":
    main()
