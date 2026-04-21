#!/usr/bin/env python3
"""
Phase 2 — 產生 8 張服務頁 og:image SVG + 1 張首頁 + 1 張 blog

設計原則：
- 1200 × 630 (Facebook/LinkedIn/Twitter 標準 og:image)
- 品牌色：deep brown #1a1410 + gold #b8923a/#d4aa52
- 服務名大字、副標、聯絡電話、logo mark
- SVG (可縮放、檔案小、品質好)
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "assets" / "og"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Logo mark — 金色算盤圖示（簡化版，從首頁抓出來）
LOGO_MARK = '''<g transform="translate(80, 70) scale(1.0)">
  <circle cx="60" cy="60" r="60" fill="#8a6e24"/>
  <circle cx="60" cy="60" r="58" fill="#b8923a"/>
  <circle cx="60" cy="60" r="56" fill="#c9a040"/>
  <circle cx="60" cy="60" r="54" fill="#d4aa52"/>
  <circle cx="60" cy="60" r="51" fill="#1a1410"/>
  <rect x="47" y="42" width="26" height="40" fill="#b8923a"/>
  <rect x="51" y="36" width="18" height="7" fill="#b8923a"/>
  <rect x="55" y="30" width="10" height="7" fill="#b8923a"/>
  <polygon points="60,22 58,30 62,30" fill="#d4aa52"/>
  <circle cx="60" cy="22" r="2" fill="#d4aa52"/>
  <g fill="#1a1410">
    <rect x="49" y="45" width="4" height="4"/><rect x="56" y="45" width="4" height="4"/><rect x="63" y="45" width="4" height="4"/>
    <rect x="49" y="51" width="4" height="4"/><rect x="56" y="51" width="4" height="4"/><rect x="63" y="51" width="4" height="4"/>
    <rect x="49" y="57" width="4" height="4"/><rect x="56" y="57" width="4" height="4"/><rect x="63" y="57" width="4" height="4"/>
    <rect x="56" y="63" width="4" height="4"/>
  </g>
  <rect x="40" y="82" width="40" height="3" fill="#b8923a"/>
  <rect x="35" y="85" width="50" height="2" fill="#b8923a" opacity="0.6"/>
</g>'''

# 背景裝飾（淡金色幾何）
BG_DECORATION = '''
<defs>
  <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#1a1410"/>
    <stop offset="100%" stop-color="#2a1f18"/>
  </linearGradient>
  <radialGradient id="glow1" cx="80%" cy="20%">
    <stop offset="0%" stop-color="#d4aa52" stop-opacity="0.18"/>
    <stop offset="50%" stop-color="#d4aa52" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="glow2" cx="15%" cy="85%">
    <stop offset="0%" stop-color="#b8923a" stop-opacity="0.12"/>
    <stop offset="50%" stop-color="#b8923a" stop-opacity="0"/>
  </radialGradient>
  <pattern id="dots" x="0" y="0" width="30" height="30" patternUnits="userSpaceOnUse">
    <circle cx="15" cy="15" r="1" fill="#d4aa52" opacity="0.08"/>
  </pattern>
</defs>
<rect width="1200" height="630" fill="url(#bg)"/>
<rect width="1200" height="630" fill="url(#glow1)"/>
<rect width="1200" height="630" fill="url(#glow2)"/>
<rect width="1200" height="630" fill="url(#dots)"/>
<!-- Top gold line -->
<rect x="0" y="0" width="1200" height="4" fill="#b8923a"/>
<!-- Bottom gold line -->
<rect x="0" y="626" width="1200" height="4" fill="#b8923a"/>'''

COMMON_FOOTER = '''
<!-- Footer bar with phone -->
<g transform="translate(80, 530)">
  <text fill="#d4aa52" font-family="'Noto Sans TC','PingFang TC',sans-serif" font-size="22" font-weight="500" letter-spacing="2">BAU QI CONSTRUCTION · 寶璣建設有限公司</text>
  <text y="34" fill="#c4b594" font-family="'Noto Sans TC','PingFang TC',sans-serif" font-size="19">新北市板橋區 · 深耕 10 年 · 律師與地政士全程陪同</text>
</g>
<g transform="translate(880, 530)">
  <rect x="0" y="0" width="240" height="62" rx="6" fill="#b8923a"/>
  <text x="120" y="28" text-anchor="middle" fill="#1a1410" font-family="'Noto Sans TC','PingFang TC',sans-serif" font-size="13" font-weight="500" letter-spacing="3">免費諮詢專線</text>
  <text x="120" y="52" text-anchor="middle" fill="#1a1410" font-family="'SF Mono',monospace" font-size="22" font-weight="700">02-2274-6789</text>
</g>'''


def make_og(filename: str, service_name_big: str, subtitle: str, detail_line: str,
            accent_tag: str = None):
    """Generate a branded og-image SVG"""
    tag_svg = ""
    if accent_tag:
        tag_svg = f'''<g transform="translate(900, 95)">
  <rect x="0" y="0" width="{20 + len(accent_tag)*24}" height="42" rx="21" fill="#b8923a"/>
  <text x="{10 + len(accent_tag)*12}" y="28" text-anchor="middle" fill="#1a1410" font-family="'Noto Sans TC','PingFang TC',sans-serif" font-size="18" font-weight="700" letter-spacing="4">{accent_tag}</text>
</g>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
{BG_DECORATION}
{LOGO_MARK}
<!-- Brand title next to logo -->
<g transform="translate(220, 95)">
  <text fill="#f7efe0" font-family="'Noto Sans TC','PingFang TC',sans-serif" font-size="30" font-weight="700" letter-spacing="4">寶璣建設</text>
  <text y="30" fill="#b8923a" font-family="'SF Pro Display',sans-serif" font-size="14" letter-spacing="3">BAU QI · 特殊土地專業代辦</text>
</g>
{tag_svg}
<!-- Main headline -->
<g transform="translate(80, 260)">
  <text fill="#f7efe0" font-family="'Noto Sans TC','PingFang TC',sans-serif" font-size="82" font-weight="800" letter-spacing="4">{service_name_big}</text>
</g>
<!-- Subtitle -->
<g transform="translate(80, 375)">
  <text fill="#d4aa52" font-family="'Noto Sans TC','PingFang TC',sans-serif" font-size="30" font-weight="400" letter-spacing="3">{subtitle}</text>
</g>
<!-- Detail line -->
<g transform="translate(80, 430)">
  <text fill="#c4b594" font-family="'Noto Sans TC','PingFang TC',sans-serif" font-size="21" font-weight="300" letter-spacing="2">{detail_line}</text>
</g>
{COMMON_FOOTER}
</svg>'''
    out = OUT_DIR / filename
    out.write_text(svg, encoding="utf-8")
    return out


# ══════════════════════════════════════════════════════════
# 10 張 og:image
# ══════════════════════════════════════════════════════════
files = []

files.append(make_og(
    "og-home.svg",
    "台灣特殊土地全方位代辦",
    "道路用地・容積移轉・祭祀公業・持份土地・兩岸繼承",
    "律師與地政士全程陪同 · 初次諮詢免費 · 5個工作天書面報價",
))

files.append(make_og(
    "og-road-land.svg",
    "道路用地買賣",
    "全台高價收購 · 公設保留地 · 既成道路",
    "建商直接收購 · 不經仲介層層剝皮 · 5日書面報價",
    accent_tag="高價收購",
))

files.append(make_og(
    "og-floor-area-ratio.svg",
    "容積移轉代辦",
    "送出基地評估 · 接受基地媒合 · 容積代金方案",
    "公共設施保留地所有人的最佳解方 · 3-6 個月完成代辦",
    accent_tag="10年經驗",
))

files.append(make_og(
    "og-rezoning-land.svg",
    "重劃地買賣",
    "市地重劃・區段徵收・抵價地處分",
    "重劃前、中、後全階段協助 · 掌握實際交易行情",
    accent_tag="仲介整合",
))

files.append(make_og(
    "og-tenancy-375.svg",
    "三七五租約解約",
    "耕地佃農合法終止租約 · 地主回收土地",
    "全台 2.3 萬筆耕地受三七五束縛 · 我們協助數百位地主脫困",
    accent_tag="地主專屬",
))

files.append(make_og(
    "og-co-ownership.svg",
    "持份土地買賣",
    "分別共有快速變現 · 土地法 34-1 處分",
    "持分 1/2 以上即可處分 · 20 天完成交易 · 免全體同意",
    accent_tag="快速變現",
))

files.append(make_og(
    "og-joint-ownership.svg",
    "公同共有處理",
    "繼承未分割土地整合 · 派下員協調",
    "解決「全體同意才能動」的死結 · 依 34-1 準用處分",
    accent_tag="產權整合",
))

files.append(make_og(
    "og-ancestral-land.svg",
    "祭祀公業",
    "派下員認定 · 法人登記 · 土地分割標售",
    "全台 9,000+ 祭祀公業 · 跨世紀產權地雷我們拆最多",
    accent_tag="專業處理",
))

files.append(make_og(
    "og-cross-strait-inheritance.svg",
    "兩岸三地繼承",
    "日據繼承 · 港澳遺囑 · 跨境不動產",
    "家族樹追溯 · 戶籍謄本比對 · 日治時期舊慣適用",
    accent_tag="跨境專家",
))

files.append(make_og(
    "og-blog.svg",
    "土地知識專欄",
    "實務專家 10 年撰寫 · 法規最新",
    "道路用地 · 容積移轉 · 共有土地 · 祭祀公業 深度解析",
    accent_tag="深度解析",
))

print(f"✅ 產生 {len(files)} 張 og:image SVG")
for f in files:
    size = f.stat().st_size
    print(f"  {f.name:40s} {size:>6} bytes")
