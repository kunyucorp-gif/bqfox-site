#!/usr/bin/env python3
"""
Phase 2: CTR 工程 — 重寫 title/description/keywords/og:image
=========================================================
針對 10 個關鍵頁面（首頁 + 8 服務頁 + blog 首頁），根據 GSC 數據和競品分析，
重寫更有吸引力、包含行動字眼的 SEO meta。

設計哲學：
- title 把「使用者想要的」放最前面（高價收購、免費諮詢、5天報價）
- description 開頭用情境/數字，中段服務內容，結尾具體 CTA
- 加 og:image meta（實際 SVG 在 assets/og/ 另外產）
- 加 og:type, twitter:card, article:modified_time

Idempotent：根據 <!-- PHASE2_MARKER --> 判斷是否已處理過
"""
import re
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).resolve().parent.parent
TODAY = datetime.now().strftime("%Y-%m-%d")

# ════════════════════════════════════════════════════════════
# 10 頁的新 meta（精心設計每一個）
# ════════════════════════════════════════════════════════════

PAGES = {
    "index.html": {
        "title": "道路用地・持份土地・祭祀公業 專業代辦｜寶璣建設 10年經驗 律師陪同",
        "description": "全台道路用地高價收購・容積移轉代辦・三七五租約解約・持份土地整合・祭祀公業出售・公同共有・兩岸繼承。新北板橋深耕10年，律師地政士全程陪同，初次諮詢免費。電洽 02-2274-6789 報價最快5個工作天。",
        "keywords": "道路用地買賣,道路用地收購,道路用地行情,公共設施保留地,容積移轉代辦,三七五租約解約,持分土地買賣,祭祀公業土地,公同共有處理,兩岸三地繼承,既成道路,新北板橋土地代辦",
        "og_image": "/assets/og/og-home.svg",
        "og_image_alt": "寶璣建設｜台灣特殊土地專業代辦",
    },
    "pages/road-land.html": {
        "title": "道路用地買賣・收購｜全台高價收購 5日書面報價｜寶璣建設",
        "description": "專收全台道路用地、既成道路、計畫道路、公設保留地。10年實務經驗、建商直接收購、不經過仲介層層剝皮，5個工作天內給您書面報價。持分比例不全也可處理，律師全程把關。電洽 02-2274-6789 免費估價。",
        "keywords": "道路用地買賣,道路用地收購,道路用地行情,既成道路買賣,計畫道路,公共設施保留地買賣,容積移轉,道路用地公告現值,道路用地賣掉,持分道路用地",
        "og_image": "/assets/og/og-road-land.svg",
        "og_image_alt": "道路用地收購｜寶璣建設",
    },
    "pages/floor-area-ratio.html": {
        "title": "容積移轉代辦｜公設保留地送出基地專業處理｜寶璣建設 10年實務",
        "description": "容積移轉代辦專家，協助公共設施保留地、道路用地所有人換取合理補償。從送出基地評估、接受基地媒合、審查文件到容積代金方案，律師與地政士全程陪同。3-6 個月完成代辦。電洽 02-2274-6789 免費諮詢。",
        "keywords": "容積移轉代辦,容積移轉流程,容積移轉費用,送出基地,接受基地,容積代金,公設保留地容積移轉,道路用地容積移轉,容積獎勵",
        "og_image": "/assets/og/og-floor-area-ratio.svg",
        "og_image_alt": "容積移轉代辦｜寶璣建設",
    },
    "pages/rezoning-land.html": {
        "title": "重劃地買賣｜市地重劃・區段徵收土地仲介｜寶璣建設",
        "description": "市地重劃區、區段徵收區土地買賣仲介。協助重劃前預售、重劃中產權整合、重劃後抵價地處分。了解您的土地在重劃計畫中的實際價值，律師全程保障交易安全。10年實務經驗，電洽 02-2274-6789。",
        "keywords": "重劃地買賣,市地重劃,區段徵收,抵價地買賣,重劃區土地,重劃前土地,重劃後土地,土地整合,都市重劃",
        "og_image": "/assets/og/og-rezoning-land.svg",
        "og_image_alt": "重劃地買賣｜寶璣建設",
    },
    "pages/tenancy-375.html": {
        "title": "三七五租約解約｜耕地佃農終止租約合法處理｜寶璣建設 10年經驗",
        "description": "三七五減租耕地地主專屬服務。協助依「耕地三七五減租條例」合法終止租約、處理佃農補償、土地回收、後續買賣或建設規劃。全台約2.3萬筆耕地受三七五束縛，我們已協助數百位地主脫困。電洽 02-2274-6789。",
        "keywords": "三七五租約解約,三七五減租,耕地三七五,佃農補償,三七五租約終止,耕地收回,佃農解約,耕地租佃條例",
        "og_image": "/assets/og/og-tenancy-375.svg",
        "og_image_alt": "三七五租約解約｜寶璣建設",
    },
    "pages/co-ownership.html": {
        "title": "持份土地買賣・租賃｜分別共有土地快速變現｜寶璣建設",
        "description": "持分土地、分別共有不動產買賣・租賃專家。依土地法第34條之1，持分1/2以上即可處分，單獨持分也能快速變現。20天完成交易付清尾款，免全體共有人同意。10年協助數百筆共有土地整合。電洽 02-2274-6789。",
        "keywords": "持分土地買賣,持份土地買賣,分別共有,應有部分,土地法34-1,共有土地買賣,持分土地行情,持分土地租賃,共有土地處分",
        "og_image": "/assets/og/og-co-ownership.svg",
        "og_image_alt": "持份土地買賣租賃｜寶璣建設",
    },
    "pages/joint-ownership.html": {
        "title": "公同共有土地處理｜繼承未分割土地整合專家｜寶璣建設",
        "description": "公同共有土地處理 10 年經驗。解決繼承未辦分割、派下員意見不一、產權40年閒置等「全體同意才能動」的死結。依土地法第34條之1準用處分，無需全體同意。律師協助文件、地政士代辦登記。電洽 02-2274-6789。",
        "keywords": "公同共有,公同共有處理,公同共有土地,繼承未分割,派下員,共有土地分割,公同共有買賣,土地法34-1準用",
        "og_image": "/assets/og/og-joint-ownership.svg",
        "og_image_alt": "公同共有處理｜寶璣建設",
    },
    "pages/ancestral-land.html": {
        "title": "祭祀公業土地處理｜派下員認定・法人登記・土地出售｜寶璣建設",
        "description": "祭祀公業土地專業處理。全台超過 9,000 個祭祀公業，掌握數千億土地資產。協助派下員身份認定、祭祀公業法人登記、土地分割、建檔申報、標售或共同處分。跨世紀產權地雷，我們拆過最多。電洽 02-2274-6789。",
        "keywords": "祭祀公業,祭祀公業土地,祭祀公業條例,派下員,祭祀公業法人,神明會土地,祭田,祭祀公業標售,祭祀公業繼承",
        "og_image": "/assets/og/og-ancestral-land.svg",
        "og_image_alt": "祭祀公業土地處理｜寶璣建設",
    },
    "pages/cross-strait-inheritance.html": {
        "title": "兩岸三地繼承｜日據繼承・港澳遺產・跨境不動產｜寶璣建設",
        "description": "台港澳中四地繼承專家。處理兩岸人民關係條例、日據時期舊慣繼承、港澳遺囑認證、跨境不動產登記等複雜案件。台灣 15 萬筆土地源自日據繼承糾紛，我們有完整家族樹追溯、戶籍謄本比對流程。電洽 02-2274-6789。",
        "keywords": "兩岸三地繼承,兩岸繼承,日據繼承,日治時期繼承,大陸繼承,港澳繼承,家督相續,招贅繼承,舊慣繼承,跨境遺產",
        "og_image": "/assets/og/og-cross-strait-inheritance.svg",
        "og_image_alt": "兩岸三地繼承｜寶璣建設",
    },
    "blog/index.html": {
        "title": "土地知識專欄｜道路用地・容積移轉・共有土地・祭祀公業 深度解析｜寶璣建設",
        "description": "寶璣建設 10 年實務撰寫的土地法律專欄。深度解析道路用地買賣、容積移轉代辦、三七五租約、持分土地、公同共有、祭祀公業、兩岸三地繼承等特殊土地處理。地主必讀、實例豐富、法規最新。",
        "keywords": "土地法律專欄,道路用地知識,容積移轉教學,三七五租約法規,持分土地法規,祭祀公業解析,公同共有說明,兩岸繼承教學,不動產法律",
        "og_image": "/assets/og/og-blog.svg",
        "og_image_alt": "土地知識專欄｜寶璣建設",
    },
}

# ════════════════════════════════════════════════════════════
# 工具函式
# ════════════════════════════════════════════════════════════

def update_meta(html: str, meta: dict, canonical_path: str) -> str:
    """Update title/desc/keywords/og tags in the HTML head"""
    # 1. title
    html = re.sub(
        r'<title>.*?</title>',
        f'<title>{meta["title"]}</title>',
        html, count=1, flags=re.I|re.S
    )

    # 2. meta description
    def replace_desc(m):
        return re.sub(
            r'content=["\'].*?["\']',
            f'content="{meta["description"]}"',
            m.group(0), count=1, flags=re.I|re.S
        )
    html = re.sub(
        r'<meta[^>]*name=["\']description["\'][^>]*>',
        replace_desc, html, count=1, flags=re.I|re.S
    )

    # 3. meta keywords
    if meta.get("keywords"):
        def replace_kw(m):
            return re.sub(
                r'content=["\'].*?["\']',
                f'content="{meta["keywords"]}"',
                m.group(0), count=1, flags=re.I|re.S
            )
        if re.search(r'<meta[^>]*name=["\']keywords["\']', html, re.I):
            html = re.sub(
                r'<meta[^>]*name=["\']keywords["\'][^>]*>',
                replace_kw, html, count=1, flags=re.I|re.S
            )
        else:
            # Insert after description
            html = re.sub(
                r'(<meta[^>]*name=["\']description["\'][^>]*>)',
                r'\1\n<meta name="keywords" content="' + meta["keywords"] + '">',
                html, count=1, flags=re.I|re.S
            )

    # 4. og:title
    og_title_tag = f'<meta property="og:title" content="{meta["title"]}">'
    if re.search(r'<meta[^>]*property=["\']og:title["\']', html, re.I):
        html = re.sub(
            r'<meta[^>]*property=["\']og:title["\'][^>]*>',
            og_title_tag, html, count=1, flags=re.I|re.S
        )

    # 5. og:description
    og_desc_tag = f'<meta property="og:description" content="{meta["description"]}">'
    if re.search(r'<meta[^>]*property=["\']og:description["\']', html, re.I):
        html = re.sub(
            r'<meta[^>]*property=["\']og:description["\'][^>]*>',
            og_desc_tag, html, count=1, flags=re.I|re.S
        )

    # 6. og:image — replace or insert
    og_image_url = f'https://www.bqfox.com{meta["og_image"]}'
    og_image_tags = (
        f'<meta property="og:image" content="{og_image_url}">\n'
        f'<meta property="og:image:alt" content="{meta["og_image_alt"]}">\n'
        f'<meta property="og:image:type" content="image/svg+xml">\n'
        f'<meta property="og:image:width" content="1200">\n'
        f'<meta property="og:image:height" content="630">\n'
        f'<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:image" content="{og_image_url}">'
    )
    if re.search(r'<meta[^>]*property=["\']og:image["\']', html, re.I):
        # remove existing og:image* and twitter:image tags, then insert fresh block
        html = re.sub(r'<meta[^>]*property=["\']og:image[^"\']*["\'][^>]*>\s*', '', html, flags=re.I)
        html = re.sub(r'<meta[^>]*name=["\']twitter:image["\'][^>]*>\s*', '', html, flags=re.I)
        html = re.sub(r'<meta[^>]*name=["\']twitter:card["\'][^>]*>\s*', '', html, flags=re.I)
        # insert after og:description
        html = re.sub(
            r'(<meta[^>]*property=["\']og:description["\'][^>]*>)',
            r'\1\n' + og_image_tags, html, count=1, flags=re.I|re.S
        )
    else:
        # insert before </head>
        html = html.replace('</head>', og_image_tags + '\n</head>', 1)

    # 7. Article:modified_time  (helps GEO)
    modified_tag = f'<meta property="article:modified_time" content="{TODAY}T00:00:00+08:00">'
    if re.search(r'<meta[^>]*property=["\']article:modified_time["\']', html, re.I):
        html = re.sub(
            r'<meta[^>]*property=["\']article:modified_time["\'][^>]*>',
            modified_tag, html, count=1, flags=re.I|re.S
        )
    else:
        html = html.replace('</head>', modified_tag + '\n</head>', 1)

    # 8. Phase 2 marker
    marker = f'<!-- PHASE2_META_UPDATED: {TODAY} -->'
    if '<!-- PHASE2_META_UPDATED' in html:
        html = re.sub(r'<!-- PHASE2_META_UPDATED:.*?-->', marker, html, count=1)
    else:
        html = html.replace('</head>', marker + '\n</head>', 1)

    return html


def main():
    processed = []
    for path, meta in PAGES.items():
        full = REPO / path
        if not full.exists():
            print(f"⚠️  Missing: {path}")
            continue
        html = full.read_text(encoding="utf-8")
        new_html = update_meta(html, meta, path)
        full.write_text(new_html, encoding="utf-8")
        processed.append((path, len(meta["title"]), len(meta["description"])))

    print(f"✅ Updated SEO meta on {len(processed)} pages")
    print()
    print(f"{'Page':<45} {'title':>8} {'desc':>8}")
    print("─" * 65)
    for p, tl, dl in processed:
        print(f"{p:<45} {tl:>8} {dl:>8}")


if __name__ == "__main__":
    main()
