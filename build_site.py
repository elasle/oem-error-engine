#!/usr/bin/env python3
"""
OEMPartDecoder / AveríasOEM — Bilingual (en-US Primary + es-US) Static Site & SEO Engine
Generates:
- /index.html (US English primary directory — targets Amazon.com DIY appliance repair market)
- /es/index.html (Spanish directory — targets US Hispanics & LatAm/Spain)
- /error/<slug>/index.html (All English & Spanish OEM error-to-part pages, preserving all existing URLs)
- /sitemap.xml (Complete XML sitemap for Google Search Console & Bing Webmaster Tools)
- /llms.txt (Structured index for AI search engines: ChatGPT Search, Perplexity, Google AI)
- /8f4b2e9c1a7d4f6e8b3c5a9d2e1f4b7c.txt (IndexNow instant indexing verification key)
- /api/errors.json (Combined public JSON data feed)
"""

import html
import json
import os
import urllib.parse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
EN_DB_PATH = os.path.join(BASE_DIR, "data", "errors_en_db.json")
ES_DB_PATH = os.path.join(BASE_DIR, "data", "errors_db.json")
DIST_DIR = os.path.join(BASE_DIR, "dist")
INDEXNOW_KEY = "8f4b2e9c1a7d4f6e8b3c5a9d2e1f4b7c"


def load_json(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_affiliate_links(item, config):
    mon = config.get("monetization", {})
    oem_brand_query = f"{item['oem_part_number']} {item['brands'][0]}"
    full_query = item.get("affiliate_search_query") or f"{item['oem_part_number']} {item['oem_part_name']}"

    encoded_oem_brand = urllib.parse.quote_plus(oem_brand_query)
    encoded_full = urllib.parse.quote_plus(full_query)

    amz_domain = mon.get("amazon_domain", "amazon.com")
    amz_tag = mon.get("amazon_tag", "onamzasleyarb-20")
    lang = item.get("lang", "es")

    # For English items, full_query is already in English and super targeted for Amazon.com
    primary_query = encoded_full if lang == "en" else encoded_oem_brand
    amazon_main_url = f"https://www.{amz_domain}/s?k={primary_query}&tag={amz_tag}"

    amz_es_domain = mon.get("amazon_es_domain", "amazon.es")
    amz_es_tag = mon.get("amazon_es_tag", amz_tag)
    amazon_es_url = f"https://www.{amz_es_domain}/s?k={encoded_full}&tag={amz_es_tag}"

    ebay_domain = mon.get("ebay_domain", "ebay.com")
    ebay_campid = mon.get("ebay_campid", "")
    ebay_url = f"https://www.{ebay_domain}/sch/i.html?_nkw={primary_query}"
    if ebay_campid:
        ebay_url += f"&mkcid=1&mkrid=711-53200-19255-0&campid={ebay_campid}&toolid=10001"

    return {
        "amazon_main": amazon_main_url,
        "amazon_es": amazon_es_url,
        "ebay": ebay_url,
    }


def get_css():
    return """
:root {
  --bg: #0f172a;
  --surface: #1e293b;
  --surface-2: #334155;
  --border: #334155;
  --text: #f8fafc;
  --muted: #94a3b8;
  --accent: #f59e0b;
  --accent-hover: #d97706;
  --green: #10b981;
  --red: #ef4444;
  --blue: #38bdf8;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  padding-bottom: 4rem;
}
a { color: var(--blue); text-decoration: none; }
a:hover { text-decoration: underline; }
.container { max-width: 980px; margin: 0 auto; padding: 0 1.25rem; }
header {
  background: rgba(30, 41, 59, 0.92);
  border-bottom: 1px solid var(--border);
  padding: 0.95rem 0;
  position: sticky;
  top: 0;
  z-index: 20;
  backdrop-filter: blur(8px);
}
.nav-inner { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; }
.logo { font-weight: 800; font-size: 1.22rem; color: var(--text); display: flex; align-items: center; gap: 0.5rem; text-decoration: none !important; }
.logo span { background: var(--accent); color: #000; padding: 0.1rem 0.45rem; border-radius: 4px; font-size: 0.8rem; font-family: monospace; }
.lang-switch { display: flex; gap: 0.5rem; align-items: center; font-size: 0.85rem; }
.lang-pill {
  padding: 0.3rem 0.65rem;
  border-radius: 6px;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  text-decoration: none !important;
  font-weight: 600;
}
.lang-pill.active { border-color: var(--accent); color: var(--accent); }
.badge-bar { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 1.5rem 0 0.75rem; }
.badge {
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  font-size: 0.8rem;
  color: var(--muted);
}
.badge.cat { color: var(--accent); border-color: rgba(245, 158, 11, 0.4); font-weight: 600; }
h1 { font-size: 1.9rem; line-height: 1.25; margin-bottom: 1rem; color: #fff; }
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.85rem;
  margin: 1.5rem 0;
}
.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem;
}
.kpi-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); }
.kpi-val { font-size: 1.15rem; font-weight: 700; margin-top: 0.25rem; }
.kpi-val.price { color: var(--green); }
.kpi-val.oem { color: var(--accent); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }

.oem-cta-box {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.98), rgba(15, 23, 42, 0.98));
  border: 2px solid var(--accent);
  border-radius: 14px;
  padding: 1.5rem;
  margin: 1.75rem 0;
  box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}
.oem-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }
.oem-code-pill {
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid var(--accent);
  color: var(--accent);
  font-family: monospace;
  font-size: 1rem;
  font-weight: 700;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
}
.btn-group { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1.25rem; }
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.9rem 1.35rem;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none !important;
  transition: transform 0.12s ease, opacity 0.12s ease;
}
.btn:hover { transform: translateY(-1px); }
.btn-amz { background: var(--accent); color: #000; flex: 2 1 280px; }
.btn-amz:hover { background: var(--accent-hover); }
.btn-ebay { background: var(--surface-2); color: #fff; border: 1px solid #475569; flex: 1 1 180px; }

.section-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}
.section-card h2 { font-size: 1.25rem; margin-bottom: 0.85rem; color: #fff; display: flex; align-items: center; gap: 0.5rem; }
.step-list { list-style: none; counter-reset: steps; }
.step-list li {
  counter-increment: steps;
  position: relative;
  padding-left: 2.5rem;
  margin-bottom: 0.9rem;
}
.step-list li::before {
  content: counter(steps);
  position: absolute;
  left: 0;
  top: 0.1rem;
  width: 1.75rem;
  height: 1.75rem;
  background: var(--surface-2);
  color: var(--accent);
  font-weight: 700;
  font-size: 0.85rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.faq-item { border-top: 1px solid var(--border); padding-top: 1rem; margin-top: 1rem; }
.faq-item:first-of-type { border-top: none; padding-top: 0; margin-top: 0; }
.faq-q { font-weight: 700; color: #fff; margin-bottom: 0.35rem; }
.faq-a { color: var(--muted); font-size: 0.95rem; }

.search-box {
  width: 100%;
  padding: 1rem 1.25rem;
  font-size: 1.05rem;
  border-radius: 10px;
  border: 2px solid var(--border);
  background: var(--surface);
  color: #fff;
  margin: 1rem 0 1.5rem;
}
.search-box:focus { outline: none; border-color: var(--accent); }
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(295px, 1fr));
  gap: 1rem;
}
.item-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: border-color 0.15s ease;
  text-decoration: none !important;
}
.item-card:hover { border-color: var(--accent); }
.item-card h3 { font-size: 1.08rem; color: #fff; margin: 0.45rem 0 0.5rem; }
.item-meta { font-size: 0.8rem; color: var(--muted); font-family: monospace; }
footer {
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
  font-size: 0.8rem;
  color: var(--muted);
  text-align: center;
}
"""


def build_schema_json_ld(item):
    lang = item.get("lang", "es")
    brands_str = " / ".join(item["brands"])
    if lang == "en":
        q1 = f"What causes {item['error_code']} on a {brands_str} {item['category'].lower()}?"
        a1 = f"{item['technical_cause']} The exact OEM replacement part number is {item['oem_part_number']} ({item['oem_part_name']})."
        howto_name = f"How to fix {brands_str} {item['error_code']} (OEM Part #{item['oem_part_number']})"
        step_label = "Step"
    else:
        q1 = f"¿Qué significa el {item['error_code']} en {item['category'].lower()} {brands_str}?"
        a1 = f"{item['technical_cause']} La pieza de recambio oficial tiene la referencia OEM {item['oem_part_number']} ({item['oem_part_name']})."
        howto_name = f"Cómo solucionar el {item['error_code']} en {brands_str} (Ref. OEM {item['oem_part_number']})"
        step_label = "Paso"

    faq_entities = [{"@type": "Question", "name": q1, "acceptedAnswer": {"@type": "Answer", "text": a1}}]
    for f in item.get("faq", []):
        faq_entities.append(
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
        )

    howto_steps = [
        {"@type": "HowToStep", "position": idx + 1, "name": f"{step_label} {idx + 1}", "text": step}
        for idx, step in enumerate(item.get("diagnostic_steps", []))
    ]

    schema = [
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_entities},
        {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": howto_name,
            "description": item["symptom"],
            "totalTime": f"PT{item.get('repair_time_minutes', 20)}M",
            "supply": [{"@type": "HowToSupply", "name": f"{item['oem_part_name']} (OEM {item['oem_part_number']})"}],
            "step": howto_steps,
        },
    ]
    return json.dumps(schema, ensure_ascii=False)


def render_error_page(item, same_lang_items, config):
    lang = item.get("lang", "es")
    brands_str = " / ".join(item["brands"])
    page_url = f"{config['site_url'].rstrip('/')}/error/{item['slug']}/"
    links = build_affiliate_links(item, config)
    schema_json = build_schema_json_ld(item)

    related = [
        x for x in same_lang_items
        if x["id"] != item["id"] and (x["category"] == item["category"] or set(x["brands"]) & set(item["brands"]))
    ][:4]

    steps_html = "\n".join(f"<li>{html.escape(s)}</li>" for s in item.get("diagnostic_steps", []))
    faq_html = "\n".join(
        f'<div class="faq-item"><div class="faq-q">{html.escape(f["q"])}</div><div class="faq-a">{html.escape(f["a"])}</div></div>'
        for f in item.get("faq", [])
    )

    has_ebay = bool(config.get("monetization", {}).get("ebay_campid", "").strip())

    if lang == "en":
        title = f"{brands_str} {item['error_code']} Fix: Exact Cause & OEM Part #{item['oem_part_number']}"
        meta_desc = (
            f"How to fix {brands_str} {item['category'].lower()} {item['error_code']}. "
            f"Symptom: {item['symptom'][:105]}... Exact OEM replacement part: {item['oem_part_number']} ({item['part_price_range']})."
        )
        home_href = "../../index.html"
        back_label = "← Search all US OEM Error Codes"
        h1_text = f"{brands_str} {item['error_code']} — Diagnostic & Exact OEM Replacement Part"
        kpi_oem = "Official OEM Part Number"
        kpi_price = "Average Part Price"
        kpi_tech = "Service Call Cost (Saved)"
        kpi_time = "DIY Install Time"
        cta_eyebrow = "Verified OEM Replacement Part That Fixes This Code"
        cta_sub = f"Primary OEM Ref: <strong>{html.escape(item['oem_part_number'])}</strong> · Cross-Ref / Alternate: {html.escape(item.get('secondary_part_number', 'N/A'))}"
        btn_amz_text = f"🛒 Check OEM Part #{html.escape(item['oem_part_number'])} on Amazon.com →"
        sec_btn_html = (
            f'<a class="btn btn-ebay" href="{html.escape(links["ebay"])}" target="_blank" rel="sponsored nofollow noopener">🔎 Find OEM Part on eBay</a>'
            if has_ebay
            else ""
        )
        cta_note = f"* Always match OEM Part <strong>{html.escape(item['oem_part_number'])}</strong> with your appliance model sticker before ordering."
        sec1_title = "⚠️ Failure Symptom & Factory Service Manual Root Cause"
        sec1_sym = "Symptom on machine:"
        sec1_cause = "Verified technical root cause:"
        sec2_title = "🔧 Step-by-Step DIY Inspection & Replacement Checklist"
        sec3_title = f"❓ Frequently Asked Questions ({item['error_code']})"
        rel_title = "Related Appliance Error Codes & OEM Parts"
        rel_cta = "View OEM Fix →"
        footer_p1 = "OEMPartDecoder / AveríasOEM — Automated Technical Error Code & OEM Part Number Lookup."
        footer_p2 = "As an Amazon Associate we earn from qualifying purchases. All OEM part numbers are used strictly for technical identification."
    else:
        title = f"{item['error_code']} {item['category']} {brands_str}: Causa y Pieza Exacta OEM ({item['oem_part_number']})"
        meta_desc = (
            f"Solución rápida al {item['error_code']} en {item['category'].lower()} {brands_str}. "
            f"Síntoma: {item['symptom'][:105]}... Pieza OEM exacta: {item['oem_part_number']} ({item['part_price_range']})."
        )
        home_href = "../../es/index.html"
        back_label = "← Buscar otro código en Español"
        h1_text = f"{item['error_code']} en {item['category']} {brands_str}: Diagnóstico y Pieza OEM"
        kpi_oem = "Referencia OEM Oficial"
        kpi_price = "Precio medio del repuesto"
        kpi_tech = "Coste Servicio Técnico"
        kpi_time = "Tiempo de sustitución"
        cta_eyebrow = "Pieza Exacta que Resuelve el Fallo"
        cta_sub = f"Ref. Principal: <strong>{html.escape(item['oem_part_number'])}</strong> · Equivalente: {html.escape(item.get('secondary_part_number', 'N/A'))}"
        btn_amz_text = f"🛒 Ver Repuesto {html.escape(item['oem_part_number'])} en Amazon.com →"
        sec_btn_html = (
            f'<a class="btn btn-ebay" href="{html.escape(links["ebay"])}" target="_blank" rel="sponsored nofollow noopener">🔎 Buscar OEM en eBay</a>'
            if has_ebay
            else ""
        )
        cta_note = f"* Comprueba siempre que el código OEM <strong>{html.escape(item['oem_part_number'])}</strong> coincida con tu modelo antes de pedir."
        sec1_title = "⚠️ Síntoma y Causa Técnica Según Manual de Servicio"
        sec1_sym = "Síntoma en la máquina:"
        sec1_cause = "Causa raíz verificada:"
        sec2_title = "🔧 Comprobación Paso a Paso Antes de Cambiar la Pieza"
        sec3_title = f"❓ Preguntas Frecuentes sobre el {item['error_code']}"
        rel_title = "Otros Códigos de Error Relacionados"
        rel_cta = "Ver ficha OEM →"
        footer_p1 = "AveríasOEM — Base de datos automatizada de códigos de avería y referencias OEM."
        footer_p2 = "Como Afiliados de Amazon obtenemos ingresos por las compras adscritas que cumplen los requisitos aplicables."

    related_html = "\n".join(
        f'<a class="item-card" href="../../error/{r["slug"]}/">'
        f'<div><span class="item-meta">{html.escape(r["category"])} · OEM {html.escape(r["oem_part_number"])}</span>'
        f'<h3>{html.escape(r["error_code"])} — {html.escape(" / ".join(r["brands"]))}</h3>'
        f'<p style="color:var(--muted);font-size:0.85rem;">{html.escape(r["oem_part_name"])}</p></div>'
        f'<span style="color:var(--accent);font-size:0.85rem;font-weight:700;margin-top:0.75rem;">{rel_cta}</span></a>'
        for r in related
    )

    models_badges = "".join(f'<span class="badge">{html.escape(m)}</span>' for m in item.get("popular_models", []))

    return f"""<!DOCTYPE html>
<html lang="{ 'en-US' if lang == 'en' else 'es' }">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(meta_desc)}">
  <link rel="canonical" href="{html.escape(page_url)}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(meta_desc)}">
  <meta property="og:type" content="article">
  <script type="application/ld+json">{schema_json}</script>
  <style>{get_css()}</style>
</head>
<body>
  <header>
    <div class="container nav-inner">
      <a href="{home_href}" class="logo">⚡ OEMPartDecoder <span>OEM DB</span></a>
      <div class="lang-switch">
        <a href="../../index.html" class="lang-pill {'active' if lang == 'en' else ''}">🇺🇸 English (US)</a>
        <a href="../../es/index.html" class="lang-pill {'active' if lang == 'es' else ''}">🇪🇸 Español</a>
      </div>
    </div>
  </header>

  <main class="container">
    <div style="margin-top:1rem;">
      <a href="{home_href}" style="font-size:0.88rem;color:var(--muted);">{back_label}</a>
    </div>

    <div class="badge-bar">
      <span class="badge cat">{html.escape(item['category'])}</span>
      <span class="badge">{html.escape(brands_str)}</span>
      {models_badges}
    </div>

    <h1>{html.escape(h1_text)}</h1>

    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">{kpi_oem}</div>
        <div class="kpi-val oem">{html.escape(item['oem_part_number'])}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">{kpi_price}</div>
        <div class="kpi-val price">{html.escape(item['part_price_range'])}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">{kpi_tech}</div>
        <div class="kpi-val" style="color:var(--red);text-decoration:line-through;">{html.escape(item.get('technician_cost_estimate', '$210 - $320'))}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">{kpi_time}</div>
        <div class="kpi-val">{item.get('repair_time_minutes', 20)} min · {html.escape(item.get('difficulty', 'Easy'))}</div>
      </div>
    </div>

    <div class="oem-cta-box">
      <div class="oem-header">
        <div>
          <div style="font-size:0.8rem;text-transform:uppercase;color:var(--accent);font-weight:700;letter-spacing:0.05em;">{cta_eyebrow}</div>
          <h2 style="font-size:1.35rem;color:#fff;margin-top:0.2rem;">{html.escape(item['oem_part_name'])}</h2>
          <p style="color:var(--muted);font-size:0.9rem;margin-top:0.25rem;">{cta_sub}</p>
        </div>
        <div class="oem-code-pill">OEM #{html.escape(item['oem_part_number'])}</div>
      </div>

      <div class="btn-group">
        <a class="btn btn-amz" href="{html.escape(links['amazon_main'])}" target="_blank" rel="sponsored nofollow noopener">
          {btn_amz_text}
        </a>
        {sec_btn_html}
      </div>
      <p style="font-size:0.75rem;color:var(--muted);margin-top:0.75rem;">
        {cta_note}
      </p>
    </div>

    <section class="section-card">
      <h2>{sec1_title}</h2>
      <p style="margin-bottom:0.85rem;"><strong>{sec1_sym}</strong> {html.escape(item['symptom'])}</p>
      <p style="color:var(--muted);"><strong>{sec1_cause}</strong> {html.escape(item['technical_cause'])}</p>
    </section>

    <section class="section-card">
      <h2>{sec2_title}</h2>
      <ol class="step-list">
        {steps_html}
      </ol>
    </section>

    <section class="section-card">
      <h2>{html.escape(sec3_title)}</h2>
      {faq_html}
    </section>

    <section style="margin-top:2rem;">
      <h2 style="font-size:1.2rem;margin-bottom:1rem;">{rel_title}</h2>
      <div class="cards-grid">
        {related_html}
      </div>
    </section>
  </main>

  <footer class="container">
    <p>{footer_p1}</p>
    <p style="margin-top:0.35rem;">{footer_p2}</p>
  </footer>
</body>
</html>
"""


def render_index_page(items, config, lang="en", prefix=""):
    categories = sorted(list({x["category"] for x in items}))
    all_label = "All Categories" if lang == "en" else "Todos"
    cat_buttons = f'<button class="badge cat" onclick="filterCat(\'\')" style="cursor:pointer;">{all_label} ({len(items)})</button>'
    for c in categories:
        count = sum(1 for x in items if x["category"] == c)
        cat_buttons += f' <button class="badge" onclick="filterCat(\'{html.escape(c)}\')" style="cursor:pointer;">{html.escape(c)} ({count})</button>'

    cards_html = []
    part_label = "OEM Part:" if lang == "en" else "Pieza:"
    cta_label = "View OEM Fix →" if lang == "en" else "Ver solución →"
    for item in items:
        brands_str = " / ".join(item["brands"])
        search_blob = f"{item['error_code']} {brands_str} {item['category']} {item['oem_part_number']} {item['oem_part_name']} {' '.join(item.get('popular_models', []))}".lower()
        cards_html.append(
            f'<a class="item-card" href="{prefix}error/{item["slug"]}/" data-cat="{html.escape(item["category"])}" data-search="{html.escape(search_blob)}">'
            f'<div>'
            f'<div style="display:flex;justify-content:space-between;align-items:center;gap:0.5rem;">'
            f'<span class="badge cat">{html.escape(item["category"])}</span>'
            f'<span class="item-meta">OEM #{html.escape(item["oem_part_number"])}</span>'
            f'</div>'
            f'<h3>{html.escape(item["error_code"])} — {html.escape(brands_str)}</h3>'
            f'<p style="color:var(--muted);font-size:0.88rem;margin-bottom:0.75rem;">{html.escape(item["symptom"][:115])}...</p>'
            f'</div>'
            f'<div style="border-top:1px solid var(--border);padding-top:0.65rem;display:flex;justify-content:space-between;align-items:center;font-size:0.82rem;">'
            f'<span style="color:var(--green);font-weight:700;">{part_label} {html.escape(item["part_price_range"])}</span>'
            f'<span style="color:var(--accent);font-weight:700;">{cta_label}</span>'
            f'</div>'
            f'</a>'
        )

    cards_joined = "\n".join(cards_html)
    base_url = config["site_url"].rstrip("/")

    if lang == "en":
        page_title = "OEMPartDecoder — Appliance Error Code to Exact OEM Replacement Part Lookup"
        meta_desc = "Instant appliance & hardware error code lookup for Whirlpool, Maytag, Samsung, LG, GE, Frigidaire, Bosch, Dyson & Roomba. Find the exact OEM replacement part number and save $200+ on service calls."
        h1_text = "Appliance Error Code → Exact OEM Replacement Part Decoder"
        sub_text = "Type the blinking error code on your machine (e.g. <strong>F5 E2</strong>, <strong>F8 E1</strong>, <strong>OE</strong>, <strong>4C</strong>, <strong>E15</strong>, <strong>Error 26</strong>), brand, or OEM part number to see the exact factory root cause and replacement part."
        placeholder = "🔍 Search error code, brand, or OEM part # (e.g. Whirlpool F8 E1, Samsung DC47-00019A, LG OE, Bosch E15, Roomba Error 26...)"
        en_href = "index.html"
        es_href = "es/index.html"
        canonical = f"{base_url}/"
    else:
        page_title = "AveríasOEM — Buscador de Códigos de Error y Referencias de Repuestos OEM"
        meta_desc = "Buscador técnico de códigos de error de lavadoras, secadoras, lavavajillas, calderas, cafeteras, impresoras 3D y patinetes con la referencia exacta del repuesto OEM."
        h1_text = "Buscador de Códigos de Error y Piezas de Repuesto OEM"
        sub_text = "Introduce el código que parpadea en tu máquina (ej. <strong>E15</strong>, <strong>F28</strong>, <strong>Error 14</strong>, <strong>OE</strong>, <strong>4C</strong>), la marca o el código de pieza para ver la causa técnica exacta y la referencia OEM del repuesto."
        placeholder = "🔍 Buscar código (ej. E15 Bosch, F28 Vaillant, Ulka EP5, Error 14 Xiaomi, 00631200...)"
        en_href = "../index.html"
        es_href = "index.html"
        canonical = f"{base_url}/es/"

    return f"""<!DOCTYPE html>
<html lang="{'en-US' if lang == 'en' else 'es'}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(page_title)}</title>
  <meta name="description" content="{html.escape(meta_desc)}">
  <link rel="canonical" href="{html.escape(canonical)}">
  <link rel="alternate" hreflang="en-US" href="{base_url}/">
  <link rel="alternate" hreflang="es" href="{base_url}/es/">
  <link rel="alternate" hreflang="x-default" href="{base_url}/">
  <style>{get_css()}</style>
</head>
<body>
  <header>
    <div class="container nav-inner">
      <a href="{en_href if lang == 'en' else es_href}" class="logo">⚡ OEMPartDecoder <span>OEM DB</span></a>
      <div class="lang-switch">
        <a href="{en_href}" class="lang-pill {'active' if lang == 'en' else ''}">🇺🇸 English (US)</a>
        <a href="{es_href}" class="lang-pill {'active' if lang == 'es' else ''}">🇪🇸 Español</a>
      </div>
    </div>
  </header>

  <main class="container" style="padding-top:2rem;">
    <h1>{h1_text}</h1>
    <p style="color:var(--muted);max-width:760px;">
      {sub_text}
    </p>

    <input type="search" id="searchInput" class="search-box" placeholder="{placeholder}" oninput="filterCards()">

    <div class="badge-bar" style="margin-top:0;margin-bottom:1.5rem;">
      {cat_buttons}
    </div>

    <div class="cards-grid" id="cardsGrid">
      {cards_joined}
    </div>
  </main>

  <footer class="container">
    <p>OEMPartDecoder / AveríasOEM — Updated automatically every night at 03:00 AM UTC.</p>
    <p style="margin-top:0.35rem;">As an Amazon Associate we earn from qualifying purchases (Tag: onamzasleyarb-20). OEM numbers are listed for technical identification.</p>
  </footer>

  <script>
    let activeCat = '';
    function filterCat(cat) {{
      activeCat = cat;
      filterCards();
    }}
    function filterCards() {{
      const q = document.getElementById('searchInput').value.toLowerCase().trim();
      const cards = document.querySelectorAll('#cardsGrid .item-card');
      cards.forEach(card => {{
        const matchCat = !activeCat || card.getAttribute('data-cat') === activeCat;
        const matchQ = !q || card.getAttribute('data-search').includes(q);
        card.style.display = (matchCat && matchQ) ? 'flex' : 'none';
      }});
    }}
  </script>
</body>
</html>
"""


def build_sitemap(all_items, config):
    base_url = config["site_url"].rstrip("/")
    today = datetime.now().strftime("%Y-%m-%d")
    urls = [
        f"  <url>\n    <loc>{base_url}/</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>",
        f"  <url>\n    <loc>{base_url}/es/</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>0.9</priority>\n  </url>",
    ]
    for item in all_items:
        lastmod = item.get("created_at", today)
        loc = f"{base_url}/error/{item['slug']}/"
        urls.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>"
        )
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n"


def build_llms_txt(en_items, es_items, config):
    base_url = config["site_url"].rstrip("/")
    lines = [
        "# OEMPartDecoder / AveríasOEM — Appliance Error Code to Exact OEM Part Number Database",
        "",
        "> Structured technical directory mapping appliance, HVAC, 3D printer, and hardware error codes to their exact factory OEM replacement part numbers and diagnostic steps.",
        "",
        "## Primary Portals",
        f"- [US English Portal]({base_url}/): {len(en_items)} verified US appliance & hardware OEM error guides",
        f"- [Spanish Portal]({base_url}/es/): {len(es_items)} verified Spanish OEM error guides",
        f"- [Full JSON API Feed]({base_url}/api/errors.json)",
        "",
        "## US English Error Code -> OEM Part Directory",
    ]
    for item in en_items:
        brands_str = "/".join(item["brands"])
        lines.append(
            f"- [{brands_str} {item['error_code']} -> OEM #{item['oem_part_number']} ({item['oem_part_name']})]({base_url}/error/{item['slug']}/): {item['symptom']}"
        )
    lines.append("")
    lines.append("## Español: Directorio Código de Error -> Pieza OEM")
    for item in es_items:
        brands_str = "/".join(item["brands"])
        lines.append(
            f"- [{brands_str} {item['error_code']} -> OEM #{item['oem_part_number']} ({item['oem_part_name']})]({base_url}/error/{item['slug']}/): {item['symptom']}"
        )
    return "\n".join(lines) + "\n"


def main():
    config = load_json(CONFIG_PATH, {})
    en_items = load_json(EN_DB_PATH, [])
    es_items = load_json(ES_DB_PATH, [])

    for x in en_items:
        x["lang"] = "en"
    for x in es_items:
        x["lang"] = x.get("lang", "es")

    all_items = en_items + es_items

    os.makedirs(DIST_DIR, exist_ok=True)
    os.makedirs(os.path.join(DIST_DIR, "es"), exist_ok=True)
    os.makedirs(os.path.join(DIST_DIR, "api"), exist_ok=True)

    # 1. Render US English Homepage (/)
    en_index_html = render_index_page(en_items, config, lang="en", prefix="")
    with open(os.path.join(DIST_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(en_index_html)

    # 2. Render Spanish Homepage (/es/)
    es_index_html = render_index_page(es_items, config, lang="es", prefix="../")
    with open(os.path.join(DIST_DIR, "es", "index.html"), "w", encoding="utf-8") as f:
        f.write(es_index_html)

    # 3. Render every individual English and Spanish error page
    for item in en_items:
        page_dir = os.path.join(DIST_DIR, "error", item["slug"])
        os.makedirs(page_dir, exist_ok=True)
        with open(os.path.join(page_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(render_error_page(item, en_items, config))

    for item in es_items:
        page_dir = os.path.join(DIST_DIR, "error", item["slug"])
        os.makedirs(page_dir, exist_ok=True)
        with open(os.path.join(page_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(render_error_page(item, es_items, config))

    # 4. Sitemap.xml, robots.txt, llms.txt & IndexNow key file
    sitemap_xml = build_sitemap(all_items, config)
    with open(os.path.join(DIST_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    robots_txt = f"User-agent: *\nAllow: /\nSitemap: {config['site_url'].rstrip('/')}/sitemap.xml\n"
    with open(os.path.join(DIST_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots_txt)

    llms_txt = build_llms_txt(en_items, es_items, config)
    with open(os.path.join(DIST_DIR, "llms.txt"), "w", encoding="utf-8") as f:
        f.write(llms_txt)

    with open(os.path.join(DIST_DIR, f"{INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
        f.write(INDEXNOW_KEY)

    # 5. Public JSON API endpoint
    with open(os.path.join(DIST_DIR, "api", "errors.json"), "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(
        f"[OK] Built {DIST_DIR}: {len(en_items)} US-English pages + {len(es_items)} Spanish pages "
        f"= {len(all_items)} total OEM pages + sitemap.xml + llms.txt + IndexNow key"
    )


if __name__ == "__main__":
    main()
