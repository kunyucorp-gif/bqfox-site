#!/usr/bin/env python3
"""
Batch 1 article generator — produces editorial-style HTML articles from content JSON.

Template matches the sample article (co-rental-fenbie.html) but externalizes all content
so we can generate 8 articles from 8 content files.
"""
import json
import html
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "blog" / "articles-v2"

# ═══════════════════════════════════════════════════════════════
#  NAV block (shared with main site)
# ═══════════════════════════════════════════════════════════════
NAV_BLOCK = '''<nav class="nav" id="nav" role="navigation" aria-label="主要導覽">
  <a href="../../index.html" class="nav-logo" aria-label="寶璣建設有限公司 首頁">
    <div class="nav-logo-mark" style="width:44px;height:44px;background:none;padding:0;border:none">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 244 244" width="44" height="44" aria-hidden="true"><circle cx="122" cy="122" r="122" fill="#8a6e24"/><circle cx="122" cy="122" r="118" fill="#b8923a"/><circle cx="122" cy="122" r="114" fill="#c9a040"/><circle cx="122" cy="122" r="110" fill="#d4aa52"/><circle cx="122" cy="122" r="104" fill="#1a1410"/><rect x="96" y="86" width="52" height="82" fill="#b8923a"/><rect x="104" y="74" width="36" height="14" fill="#b8923a"/><rect x="112" y="62" width="20" height="14" fill="#b8923a"/><polygon points="122,46 118,62 126,62" fill="#d4aa52"/><circle cx="122" cy="46" r="3.5" fill="#d4aa52"/><g fill="#1a1410"><rect x="102" y="94" width="9" height="8"/><rect x="116" y="94" width="9" height="8"/><rect x="130" y="94" width="9" height="8"/><rect x="102" y="107" width="9" height="8"/><rect x="116" y="107" width="9" height="8"/><rect x="130" y="107" width="9" height="8"/><rect x="102" y="120" width="9" height="8"/><rect x="116" y="120" width="9" height="8"/><rect x="130" y="120" width="9" height="8"/><rect x="116" y="133" width="9" height="8"/></g><rect x="82" y="168" width="80" height="6" fill="#b8923a"/></svg>
    </div>
    <div class="nav-logo-text">
      <strong>寶璣建設有限公司</strong>
      <small>BAU QI CONSTRUCTION CO, LTD</small>
    </div>
  </a>
  <div class="nav-menu" style="margin-left: auto;">
    <a href="../../index.html" class="nav-link">首頁</a>
    <a href="../index.html" class="nav-link">知識專欄</a>
    <a href="../../pages/co-ownership.html" class="nav-link">持分土地買賣</a>
  </div>
  <div class="nav-actions">
    <a href="tel:0222746789" class="nav-tel">☎ 02-2274-6789</a>
    <a href="https://lin.ee/wedzic3" class="nav-line-btn">● LINE 諮詢</a>
  </div>
</nav>'''


def render_body_block(block):
    """Render one body block. Block is a dict with 'type' and data."""
    t = block["type"]
    if t == "lede":
        return f'<p class="lede">{block["text"]}</p>'
    if t == "h2":
        return f'<h2 id="{block.get("id","")}">{block["text"]}</h2>'
    if t == "h3":
        return f'<h3>{block["text"]}</h3>'
    if t == "p":
        return f'<p>{block["text"]}</p>'
    if t == "ul":
        items = "\n".join(f'        <li>{i}</li>' for i in block["items"])
        return f'      <ul>\n{items}\n      </ul>'
    if t == "ol":
        items = "\n".join(f'        <li>{i}</li>' for i in block["items"])
        return f'      <ol>\n{items}\n      </ol>'
    if t == "callout":
        label = block.get("label", "")
        body = block["text"]
        return f'''<div class="art-callout">
      <span class="callout-label">{label}</span>
      {body}
    </div>'''
    if t == "case":
        label = block.get("label", "CASE STUDY · 化名改編")
        title = block["title"]
        paras = "\n".join(f'      <p>{p}</p>' for p in block["paragraphs"])
        return f'''<div class="art-case">
      <div class="case-label">{label}</div>
      <h4>{title}</h4>
{paras}
    </div>'''
    if t == "takeaway":
        return f'<p class="art-takeaway">{block["text"]}</p>'
    if t == "related":
        cards_html = ""
        for c in block["cards"]:
            cards_html += f'''        <a href="{c["url"]}" class="art-related-card">
          <h4>{c["title"]}</h4>
          <p>{c["desc"]}</p>
        </a>\n'''
        return f'''<div class="art-related">
      <h3>相關服務</h3>
      <div class="art-related-grid">
{cards_html}      </div>
    </div>'''
    raise ValueError(f"Unknown block type: {t}")


def render_faqs_html(faqs):
    out = ['<h2 id="faq">常見問題</h2>', '<div class="art-faq-list">']
    for i, f in enumerate(faqs):
        opn = " open" if i == 0 else ""
        out.append(f'''      <details class="art-faq-item"{opn}>
        <summary>{f["q"]}</summary>
        <div class="a">{f["a"]}</div>
      </details>''')
    out.append('</div>')
    return "\n    ".join(out)


def render_faq_schema(faqs):
    entities = []
    for f in faqs:
        entities.append({
            "@type": "Question",
            "name": f["q"],
            "acceptedAnswer": {"@type": "Answer", "text": f["a"]}
        })
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities
    }, ensure_ascii=False, separators=(',', ':'))


def render_article_schema(meta):
    """Article + WebPage combined"""
    url = f"https://www.bqfox.com/blog/articles/{meta['slug']}.html"
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "@id": f"{url}#article",
        "headline": meta["title"],
        "description": meta["description"],
        "image": f"https://www.bqfox.com{meta.get('og_image','/assets/og/og-co-ownership.svg')}",
        "author": {"@type": "Organization", "@id": "https://www.bqfox.com/#org", "name": "寶璣建設有限公司"},
        "publisher": {
            "@type": "Organization", "@id": "https://www.bqfox.com/#org", "name": "寶璣建設有限公司",
            "logo": {"@type": "ImageObject", "url": "https://www.bqfox.com/assets/logo.svg"}
        },
        "datePublished": "2026-04-22",
        "dateModified": "2026-04-22",
        "inLanguage": "zh-TW",
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "about": {"@type": "Thing", "name": meta["topic"]},
        "keywords": meta["keywords"],
    }
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))


def render_breadcrumb_schema(meta):
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首頁", "item": "https://www.bqfox.com/"},
            {"@type": "ListItem", "position": 2, "name": "土地知識專欄", "item": "https://www.bqfox.com/blog/"},
            {"@type": "ListItem", "position": 3, "name": meta["category"]},
            {"@type": "ListItem", "position": 4, "name": meta["title_short"]},
        ]
    }
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))


ARTICLE_STYLE = '''<style>
  /* Article-specific styles */
  .art-header { padding-block: var(--ed-sp-6) var(--ed-sp-5); }
  .art-breadcrumb { font-family: var(--mono-ed); font-size: 0.72rem; letter-spacing: 0.2em; color: var(--ink-faint); margin-bottom: var(--ed-sp-3); }
  .art-breadcrumb a { color: var(--ink-faint); text-decoration: none; }
  .art-breadcrumb a:hover { color: var(--gold-ed); }
  .art-breadcrumb span { color: var(--gold-ed); }

  .art-title { font-family: var(--serif-ed); font-size: clamp(2.2rem, 5vw, 3.6rem); font-weight: 800; line-height: 1.12; letter-spacing: -0.015em; color: var(--ink); text-wrap: balance; }
  .art-title em { font-style: italic; font-weight: 500; color: var(--gold-ed); }

  .art-subtitle { font-family: var(--serif-ed); font-size: clamp(1.15rem, 2vw, 1.4rem); line-height: 1.6; color: var(--ink-mid); margin-top: var(--ed-sp-3); max-width: 38em; font-weight: 400; }

  .art-meta { display: flex; align-items: center; gap: var(--ed-sp-3); margin-top: var(--ed-sp-4); padding-top: var(--ed-sp-3); border-top: 1px solid var(--rule); font-family: var(--mono-ed); font-size: 0.78rem; letter-spacing: 0.12em; color: var(--ink-faint); text-transform: uppercase; flex-wrap: wrap; }
  .art-meta .dot { color: var(--gold-ed); }

  .art-body { padding-block: var(--ed-sp-5); }
  .art-body > * { max-width: 720px; margin-inline: auto; }
  .art-body h2 { font-family: var(--serif-ed); font-size: clamp(1.6rem, 3vw, 2.1rem); font-weight: 700; line-height: 1.25; color: var(--ink); margin: var(--ed-sp-6) auto var(--ed-sp-3) auto; letter-spacing: -0.005em; }
  .art-body h2::before { content: ""; display: block; width: 3rem; height: 2px; background: var(--gold-ed); margin-bottom: var(--ed-sp-2); }
  .art-body h3 { font-family: var(--sans-ed); font-size: 1.25rem; font-weight: 700; line-height: 1.4; color: var(--ink); margin: var(--ed-sp-4) auto var(--ed-sp-2) auto; }
  .art-body p { font-size: 1.05rem; line-height: 1.9; color: var(--ink-mid); margin-bottom: var(--ed-sp-3); }
  .art-body p strong { color: var(--ink); font-weight: 600; }
  .art-body p em { font-style: italic; color: var(--gold-ed-dk); }
  .art-body ul, .art-body ol { padding-left: 1.5em; margin-bottom: var(--ed-sp-3); }
  .art-body li { font-size: 1.05rem; line-height: 1.8; color: var(--ink-mid); margin-bottom: 0.5rem; }

  .art-body .lede { font-family: var(--serif-ed); font-size: clamp(1.15rem, 2vw, 1.35rem); line-height: 1.7; color: var(--ink); font-weight: 400; margin-top: var(--ed-sp-3); margin-bottom: var(--ed-sp-4); }
  .art-body .lede::first-letter { font-family: var(--serif-ed); font-size: 4em; font-weight: 800; float: left; line-height: 0.85; padding: 0.05em 0.12em 0 0; color: var(--gold-ed); }

  .art-case { margin: var(--ed-sp-4) auto; padding: var(--ed-sp-4); background: var(--paper-dark); border-left: 3px solid var(--gold-ed); border-radius: 2px; }
  .art-case .case-label { font-family: var(--mono-ed); font-size: 0.72rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--gold-ed); font-weight: 600; margin-bottom: var(--ed-sp-2); }
  .art-case h4 { font-family: var(--serif-ed); font-size: 1.2rem; font-weight: 600; color: var(--ink); margin-bottom: var(--ed-sp-2); }
  .art-case p { font-size: 0.98rem; line-height: 1.75; color: var(--ink-mid); margin-bottom: var(--ed-sp-2); }
  .art-case p:last-child { margin-bottom: 0; }

  .art-callout { margin: var(--ed-sp-4) auto; padding: var(--ed-sp-3) var(--ed-sp-4); background: #faf6ec; border: 1px solid var(--rule); border-radius: 2px; }
  .art-callout strong { color: var(--ink); }
  .art-callout .callout-label { font-family: var(--mono-ed); font-size: 0.72rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--ink-faint); margin-bottom: var(--ed-sp-2); display: block; }

  .art-takeaway { margin: var(--ed-sp-5) auto; font-family: var(--serif-ed); font-size: clamp(1.3rem, 2.4vw, 1.7rem); font-style: italic; line-height: 1.5; color: var(--ink); padding: var(--ed-sp-3) 0; border-top: 1px solid var(--ink); border-bottom: 1px solid var(--ink); text-align: center; max-width: 32em; }

  .art-faq-list { margin-top: var(--ed-sp-3); }
  .art-faq-item { border-bottom: 1px solid var(--rule); padding: var(--ed-sp-3) 0; }
  .art-faq-item summary { font-family: var(--serif-ed); font-size: 1.15rem; font-weight: 600; color: var(--ink); cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; padding: 0.25rem 0; }
  .art-faq-item summary::-webkit-details-marker { display: none; }
  .art-faq-item summary::after { content: "+"; font-family: var(--serif-ed); font-size: 1.6rem; color: var(--gold-ed); font-weight: 300; flex-shrink: 0; line-height: 1; }
  .art-faq-item[open] summary::after { content: "−"; }
  .art-faq-item .a { padding: 1rem 0 0.5rem 0; color: var(--ink-mid); line-height: 1.8; font-size: 1rem; }

  .art-related { margin: var(--ed-sp-6) auto; padding: var(--ed-sp-4); background: var(--paper-dark); border-radius: 3px; }
  .art-related h3 { font-family: var(--sans-ed); font-size: 0.88rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--ink-faint); margin-bottom: var(--ed-sp-3); font-weight: 600; }
  .art-related-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }
  .art-related-card { background: var(--paper); padding: 1.25rem; border-radius: 2px; text-decoration: none; transition: transform 0.2s; display: block; }
  .art-related-card:hover { transform: translateY(-2px); }
  .art-related-card h4 { font-family: var(--serif-ed); font-size: 1.15rem; font-weight: 600; color: var(--ink); margin-bottom: 0.25rem; }
  .art-related-card p { font-size: 0.9rem; color: var(--ink-faint); line-height: 1.6; }

  .art-cta { background: var(--ink); color: var(--paper); padding: var(--ed-sp-6) var(--ed-sp-4); text-align: center; margin-top: var(--ed-sp-6); }
  .art-cta h3 { font-family: var(--serif-ed); font-size: clamp(1.8rem, 3vw, 2.4rem); font-weight: 700; color: var(--paper); margin-bottom: var(--ed-sp-2); }
  .art-cta h3 em { font-style: italic; color: var(--gold-ed-lt); font-weight: 500; }
  .art-cta p { color: rgba(250,246,236,.7); font-size: 1.05rem; line-height: 1.7; margin-inline: auto; margin-bottom: var(--ed-sp-3); max-width: 32em; }
  .art-cta .cta-buttons { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }
  .art-cta a { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.9rem 1.75rem; font-size: 1rem; font-weight: 600; letter-spacing: 0.05em; text-decoration: none; border-radius: 2px; }
  .art-cta a.primary { background: var(--gold-ed); color: var(--ink); }
  .art-cta a.secondary { background: transparent; color: var(--paper); border: 1px solid var(--gold-ed-lt); }
  .art-cta a.line { background: #06c755; color: #fff; }
</style>'''


def build_article(meta, body_blocks, faqs, cta):
    """Build complete HTML article"""
    url = f"https://www.bqfox.com/blog/articles/{meta['slug']}.html"

    head = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">

<title>{meta["title"]}｜寶璣建設</title>
<meta name="description" content="{meta["description"]}">
<meta name="keywords" content="{meta["keywords"]}">
<meta name="author" content="寶璣建設有限公司">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{url}">

<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{meta["title"]}">
<meta property="og:description" content="{meta["description"]}">
<meta property="og:image" content="https://www.bqfox.com{meta.get("og_image","/assets/og/og-co-ownership.svg")}">
<meta property="og:image:type" content="image/svg+xml">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="寶璣建設有限公司">
<meta property="og:locale" content="zh_TW">
<meta property="article:published_time" content="2026-04-22T00:00:00+08:00">
<meta property="article:modified_time" content="2026-04-22T00:00:00+08:00">
<meta property="article:section" content="{meta["category"]}">
<meta property="article:tag" content="{meta["keywords"]}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://www.bqfox.com{meta.get("og_image","/assets/og/og-co-ownership.svg")}">

<!-- JSON-LD Schemas (GEO) -->
<script type="application/ld+json">{render_article_schema(meta)}</script>
<script type="application/ld+json">{render_faq_schema(faqs)}</script>
<script type="application/ld+json">{render_breadcrumb_schema(meta)}</script>

<link rel="stylesheet" href="../../assets/style.css">
<link rel="stylesheet" href="../../assets/editorial.css">

{ARTICLE_STYLE}

</head>
<body class="editorial">

{NAV_BLOCK}

<article style="padding-top: var(--nav-h);">

  <header class="art-header ed-wrap-narrow">
    <nav class="art-breadcrumb" aria-label="麵包屑">
      <a href="../../">首頁</a>
      <span>›</span>
      <a href="../index.html">土地知識專欄</a>
      <span>›</span>
      <a href="#">{meta["category"]}</a>
      <span>›</span>
      {meta["title_short"]}
    </nav>

    <h1 class="art-title">
      {meta["h1"]}
    </h1>

    <p class="art-subtitle">
      {meta["subtitle"]}
    </p>

    <div class="art-meta">
      <span>{meta["category"]}</span>
      <span class="dot">·</span>
      <span>2026.04.22 · 約 {meta.get("read_time",10)} 分鐘閱讀</span>
      <span class="dot">·</span>
      <span>寶璣建設 編輯部</span>
    </div>
  </header>

  <div class="art-body ed-wrap-narrow">
'''

    body_html = ""
    for b in body_blocks:
        body_html += "    " + render_body_block(b) + "\n\n"

    faq_html = render_faqs_html(faqs)

    cta_html = f'''  <section class="art-cta">
    <div class="ed-wrap-narrow">
      <h3>{cta["headline"]}</h3>
      <p>{cta["text"]}</p>
      <div class="cta-buttons">
        <a href="tel:0222746789" class="primary">☎ 02-2274-6789</a>
        <a href="https://lin.ee/wedzic3" class="line">● LINE 諮詢</a>
        <a href="{cta["service_url"]}" class="secondary">{cta["service_label"]}</a>
      </div>
    </div>
  </section>'''

    footer = '''</article>

<div class="ed-float-cta">
  <a href="tel:0222746789" class="phone">☎ 02-2274-6789</a>
  <a href="https://lin.ee/wedzic3" class="line">LINE 諮詢</a>
</div>

<footer style="background: var(--paper-dark); padding: 2rem; text-align: center;">
  <div class="ed-small" style="line-height: 2;">
    寶璣建設有限公司 · 統一編號 94157953 · 新北市板橋區南雅南路二段 144 巷 73 號<br>
    © 2026 BAU QI CONSTRUCTION CO, LTD. All rights reserved.
  </div>
</footer>

<script>
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in'); });
  }, { threshold: 0.1 });
  document.querySelectorAll('.ed-reveal').forEach(el => io.observe(el));
</script>
</body>
</html>
'''

    return head + body_html + "    " + faq_html + "\n\n  </div>\n\n" + cta_html + "\n\n" + footer


def generate_from_json(json_path):
    """Load a content JSON and write the article HTML"""
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    meta = data["meta"]
    html_out = build_article(meta, data["body"], data["faqs"], data["cta"])
    out_path = OUT_DIR / f"{meta['slug']}.html"
    out_path.write_text(html_out, encoding="utf-8")
    return out_path, len(html_out)


if __name__ == "__main__":
    import sys
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    content_dir = REPO / "scripts" / "articles-content"
    jsons = sorted(content_dir.glob("*.json"))
    total_size = 0
    for j in jsons:
        out, size = generate_from_json(j)
        total_size += size
        print(f"  ✓ {out.name}  ({size:,} bytes)")
    print(f"\n✅ Generated {len(jsons)} articles · total {total_size:,} bytes")
