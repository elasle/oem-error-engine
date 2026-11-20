#!/usr/bin/env python3
"""
AveríasOEM Static Site & SEO Engine
Genera páginas técnicas hiper-específicas [Marca + Modelo + Código de Error -> Pieza OEM]
con datos estructurados Schema.org (FAQPage + HowTo), enlaces de afiliado automáticos,
sitemap.xml y feed JSON.
"""

import html
import json
import os
import urllib.parse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
DB_PATH = os.path.join(BASE_DIR, "data", "errors_db.json")
DIST_DIR = os.path.join(BASE_DIR, "dist")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_affiliate_links(item, config):
    mon = config.get("monetization", {})
    query = item.get("affiliate_search_query") or f"{item['oem_part_number']} {item['oem_part_name']}"
    encoded_q = urllib.parse.quote_plus(query)
    encoded_oem = urllib.parse.quote_plus(f"{item['oem_part_number']} {item['brands'][0]}")

    amz_domain = mon.get("amazon_domain", "amazon.es")
    amz_tag = mon.get("amazon_tag", "averiasoem-21")
    amazon_url = f"https://www.{amz_domain}/s?k={encoded_q}&tag={amz_tag}"

    amz_us_domain = mon.get("amazon_us_domain", "amazon.com")
    amz_us_tag = mon.get("amazon_us_tag", "averiasoem-20")
    amazon_us_url = f"https://www.{amz_us_domain}/s?k={encoded_oem}&tag={amz_us_tag}"

    ebay_domain = mon.get("ebay_domain", "ebay.es")
    ebay_campid = mon.get("ebay_campid", "")
    ebay_url = f"https://www.{ebay_domain}/sch/i.html?_nkw={encoded_q}"
    if ebay_campid:
        ebay_url += f"&mkcid=1&mkrid=1185-53479-19255-0&campid={ebay_campid}&toolid=10001"

    ali_url = f"https://es.aliexpress.com/w/wholesale-{urllib.parse.quote(item['oem_part_number'])}.html"

    return {
        "amazon_es": amazon_url,
        "amazon_us": amazon_us_url,
        "ebay": ebay_url,
        "aliexpress": ali_url,
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
.container { max-width: 960px; margin: 0 auto; padding: 0 1.25rem; }
header {
  background: rgba(30, 41, 59, 0.9);
  border-bottom: 1px solid var(--border);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 20;
  backdrop-filter: blur(8px);
}
.nav-inner { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; }
.logo { font-weight: 800; font-size: 1.25rem; color: var(--text); display: flex; align-items: center; gap: 0.5rem; }
.logo span { background: var(--accent); color: #000; padding: 0.1rem 0.45rem; border-radius: 4px; font-size: 0.85rem; font-family: monospace; }
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
  padding: 0.85rem 1.35rem;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none !important;
  transition: transform 0.12s ease, opacity 0.12s ease;
}
.btn:hover { transform: translateY(-1px); }
.btn-amz { background: var(--accent); color: #000; flex: 1 1 260px; }
.btn-amz:hover { background: var(--accent-hover); }
.btn-ebay { background: var(--surface-2); color: #fff; border: 1px solid #475569; flex: 1 1 180px; }
.btn-ali { background: #1e293b; color: var(--muted); border: 1px solid var(--border); flex: 1 1 180px; }

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
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
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
}
.item-card:hover { border-color: var(--accent); }
.item-card h3 { font-size: 1.1rem; color: #fff; margin: 0.4rem 0 0.5rem; }
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


def build_schema_json_ld(item, page_url):
    faq_entities = [
        {
            "@type": "Question",
            "name": f"¿Qué significa el {item['error_code']} en {item['category'].lower()} {' / '.join(item['brands'])}?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"{item['technical_cause']} La pieza de recambio oficial tiene la referencia OEM {item['oem_part_number']} ({item['oem_part_name']}).",
            },
        }
    ]
    for f in item.get("faq", []):
        faq_entities.append(
            {
                "@type": "Question",
                "name": f["q"],
                "acceptedAnswer": {"@type": "Answer", "text": f["a"]},
            }
        )

    howto_steps = [
        {
            "@type": "HowToStep",
            "position": idx + 1,
            "name": f"Paso {idx + 1}",
            "text": step,
        }
        for idx, step in enumerate(item.get("diagnostic_steps", []))
    ]

    schema = [
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_entities,
        },
        {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": f"Cómo solucionar el {item['error_code']} en {' / '.join(item['brands'])} (Ref. OEM {item['oem_part_number']})",
            "description": item["symptom"],
            "totalTime": f"PT{item.get('repair_time_minutes', 20)}M",
            "supply": [
                {
                    "@type": "HowToSupply",
                    "name": f"{item['oem_part_name']} (OEM {item['oem_part_number']})",
                }
            ],
            "step": howto_steps,
        },
    ]
    return json.dumps(schema, ensure_ascii=False)


def render_error_page(item, all_items, config):
    brands_str = " / ".join(item["brands"])
    title = f"{item['error_code']} {item['category']} {brands_str}: Causa y Pieza Exacta OEM ({item['oem_part_number']})"
    meta_desc = (
        f"Solución rápida al {item['error_code']} en {item['category'].lower()} {brands_str}. "
        f"Síntoma: {item['symptom'][:110]}... Pieza OEM exacta: {item['oem_part_number']} ({item['part_price_range']})."
    )
    page_url = f"{config['site_url'].rstrip('/')}/error/{item['slug']}/"
    links = build_affiliate_links(item, config)
    schema_json = build_schema_json_ld(item, page_url)

    related = [
        x for x in all_items
        if x["id"] != item["id"] and (x["category"] == item["category"] or set(x["brands"]) & set(item["brands"]))
    ][:4]

    steps_html = "\n".join(f"<li>{html.escape(s)}</li>" for s in item.get("diagnostic_steps", []))
    faq_html = "\n".join(
        f'<div class="faq-item"><div class="faq-q">{html.escape(f["q"])}</div><div class="faq-a">{html.escape(f["a"])}</div></div>'
        for f in item.get("faq", [])
    )
    related_html = "\n".join(
        f'<a class="item-card" href="../../error/{r["slug"]}/">'
        f'<div><span class="item-meta">{html.escape(r["category"])} · OEM {html.escape(r["oem_part_number"])}</span>'
        f'<h3>{html.escape(r["error_code"])} — {html.escape(" / ".join(r["brands"]))}</h3>'
        f'<p style="color:var(--muted);font-size:0.85rem;">{html.escape(r["oem_part_name"])}</p></div>'
        f'<span style="color:var(--accent);font-size:0.85rem;font-weight:700;margin-top:0.75rem;">Ver ficha OEM →</span></a>'
        for r in related
    )

    models_badges = "".join(f'<span class="badge">{html.escape(m)}</span>' for m in item.get("popular_models", []))

    return f"""<!DOCTYPE html>
<html lang="es">
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
      <a href="../../index.html" class="logo">⚡ {html.escape(config['site_name'])} <span>OEM DB</span></a>
      <a href="../../index.html" style="font-size:0.9rem;color:var(--muted);">← Buscar otro código de error</a>
    </div>
  </header>

  <main class="container">
    <div class="badge-bar">
      <span class="badge cat">{html.escape(item['category'])}</span>
      <span class="badge">Marcas: {html.escape(brands_str)}</span>
      {models_badges}
    </div>

    <h1>{html.escape(item['error_code'])} en {html.escape(item['category'])} {html.escape(brands_str)}: Diagnóstico y Pieza OEM</h1>

    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Referencia OEM Oficial</div>
        <div class="kpi-val oem">{html.escape(item['oem_part_number'])}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Precio medio del repuesto</div>
        <div class="kpi-val price">{html.escape(item['part_price_range'])}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Coste Servicio Técnico</div>
        <div class="kpi-val" style="color:var(--red);text-decoration:line-through;">{html.escape(item.get('technician_cost_estimate', '120€ - 180€'))}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Tiempo de sustitución</div>
        <div class="kpi-val">{item.get('repair_time_minutes', 20)} min · {html.escape(item.get('difficulty', 'Fácil'))}</div>
      </div>
    </div>

    <div class="oem-cta-box">
      <div class="oem-header">
        <div>
          <div style="font-size:0.8rem;text-transform:uppercase;color:var(--accent);font-weight:700;letter-spacing:0.05em;">Pieza Exacta que Resuelve el Fallo</div>
          <h2 style="font-size:1.35rem;color:#fff;margin-top:0.2rem;">{html.escape(item['oem_part_name'])}</h2>
          <p style="color:var(--muted);font-size:0.9rem;margin-top:0.25rem;">Ref. Principal: <strong>{html.escape(item['oem_part_number'])}</strong> · Equivalente: {html.escape(item.get('secondary_part_number', 'N/A'))}</p>
        </div>
        <div class="oem-code-pill">OEM #{html.escape(item['oem_part_number'])}</div>
      </div>

      <div class="btn-group">
        <a class="btn btn-amz" href="{html.escape(links['amazon_es'])}" target="_blank" rel="sponsored nofollow noopener">
          🛒 Ver Repuesto {html.escape(item['oem_part_number'])} en Amazon →
        </a>
        <a class="btn btn-ebay" href="{html.escape(links['ebay'])}" target="_blank" rel="sponsored nofollow noopener">
          🔎 Buscar OEM en eBay
        </a>
        <a class="btn btn-ali" href="{html.escape(links['aliexpress'])}" target="_blank" rel="sponsored nofollow noopener">
          📦 Comparar en AliExpress
        </a>
      </div>
      <p style="font-size:0.75rem;color:var(--muted);margin-top:0.75rem;">
        * Comprueba siempre que el código OEM <strong>{html.escape(item['oem_part_number'])}</strong> coincida con la etiqueta de tu máquina antes de pedir.
      </p>
    </div>

    <section class="section-card">
      <h2>⚠️ Síntoma y Causa Técnica Según Manual de Servicio</h2>
      <p style="margin-bottom:0.85rem;"><strong>Síntoma en la máquina:</strong> {html.escape(item['symptom'])}</p>
      <p style="color:var(--muted);"><strong>Causa raíz verificada:</strong> {html.escape(item['technical_cause'])}</p>
    </section>

    <section class="section-card">
      <h2>🔧 Comprobación Paso a Paso Antes de Cambiar la Pieza</h2>
      <ol class="step-list">
        {steps_html}
      </ol>
    </section>

    <section class="section-card">
      <h2>❓ Preguntas Frecuentes sobre el {html.escape(item['error_code'])}</h2>
      {faq_html}
    </section>

    <section style="margin-top:2rem;">
      <h2 style="font-size:1.2rem;margin-bottom:1rem;">Otros Códigos de Error Relacionados</h2>
      <div class="cards-grid">
        {related_html}
      </div>
    </section>
  </main>

  <footer class="container">
    <p>{html.escape(config['site_name'])} — Base de datos automatizada de códigos de avería y referencias OEM.</p>
    <p style="margin-top:0.35rem;">Participamos en el Programa de Afiliados de Amazon UE y eBay Partner Network. Las referencias OEM son propiedad de sus respectivos fabricantes y se muestran únicamente con fines de identificación técnica.</p>
  </footer>
</body>
</html>
"""


def render_index_page(items, config):
    categories = sorted(list({x["category"] for x in items}))
    cat_buttons = '<button class="badge cat" onclick="filterCat(\'\')" style="cursor:pointer;">Todos (' + str(len(items)) + ')</button>'
    for c in categories:
        count = sum(1 for x in items if x["category"] == c)
        cat_buttons += f' <button class="badge" onclick="filterCat(\'{html.escape(c)}\')" style="cursor:pointer;">{html.escape(c)} ({count})</button>'

    cards_html = []
    for item in items:
        brands_str = " / ".join(item["brands"])
        search_blob = f"{item['error_code']} {brands_str} {item['category']} {item['oem_part_number']} {item['oem_part_name']} {' '.join(item.get('popular_models', []))}".lower()
        cards_html.append(
            f'<a class="item-card" href="error/{item["slug"]}/" data-cat="{html.escape(item["category"])}" data-search="{html.escape(search_blob)}">'
            f'<div>'
            f'<div style="display:flex;justify-content:space-between;align-items:center;gap:0.5rem;">'
            f'<span class="badge cat">{html.escape(item["category"])}</span>'
            f'<span class="item-meta">OEM #{html.escape(item["oem_part_number"])}</span>'
            f'</div>'
            f'<h3>{html.escape(item["error_code"])} — {html.escape(brands_str)}</h3>'
            f'<p style="color:var(--muted);font-size:0.88rem;margin-bottom:0.75rem;">{html.escape(item["symptom"][:115])}...</p>'
            f'</div>'
            f'<div style="border-top:1px solid var(--border);padding-top:0.65rem;display:flex;justify-content:space-between;align-items:center;font-size:0.82rem;">'
            f'<span style="color:var(--green);font-weight:700;">Pieza: {html.escape(item["part_price_range"])}</span>'
            f'<span style="color:var(--accent);font-weight:700;">Ver solución →</span>'
            f'</div>'
            f'</a>'
        )

    cards_joined = "\n".join(cards_html)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(config['site_name'])} — {html.escape(config['site_tagline'])}</title>
  <meta name="description" content="Buscador técnico de códigos de error de calderas, lavavajillas, lavadoras, cafeteras, impresoras 3D y patinetes con la referencia exacta del repuesto OEM.">
  <style>{get_css()}</style>
</head>
<body>
  <header>
    <div class="container nav-inner">
      <a href="index.html" class="logo">⚡ {html.escape(config['site_name'])} <span>OEM DB</span></a>
      <span style="font-size:0.85rem;color:var(--muted);">{len(items)} fichas técnicas OEM verificadas</span>
    </div>
  </header>

  <main class="container" style="padding-top:2rem;">
    <h1>Buscador de Códigos de Error y Piezas OEM</h1>
    <p style="color:var(--muted);max-width:720px;">
      Introduce el código que parpadea en tu máquina (ej. <strong>E15</strong>, <strong>F28</strong>, <strong>Error 14</strong>, <strong>OE</strong>), la marca o el código de pieza para ver la causa técnica exacta y la referencia OEM del repuesto sin pagar servicio técnico.
    </p>

    <input type="search" id="searchInput" class="search-box" placeholder="🔍 Buscar código (ej. E15 Bosch, F28 Vaillant, Ulka EP5, Error 14 Xiaomi, 00631200...)" oninput="filterCards()">

    <div class="badge-bar" style="margin-top:0;margin-bottom:1.5rem;">
      {cat_buttons}
    </div>

    <div class="cards-grid" id="cardsGrid">
      {cards_joined}
    </div>
  </main>

  <footer class="container">
    <p>{html.escape(config['site_name'])} — Actualizado automáticamente cada madrugada.</p>
    <p style="margin-top:0.35rem;">Participamos en programas de afiliación (Amazon EU / eBay Partner Network). Las referencias OEM se facilitan para identificación técnica de recambios.</p>
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


def build_sitemap(items, config):
    base_url = config["site_url"].rstrip("/")
    today = datetime.now().strftime("%Y-%m-%d")
    urls = [
        f"  <url>\n    <loc>{base_url}/</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>"
    ]
    for item in items:
        lastmod = item.get("created_at", today)
        loc = f"{base_url}/error/{item['slug']}/"
        urls.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>"
        )
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n"


def main():
    config = load_json(CONFIG_PATH)
    items = load_json(DB_PATH)

    os.makedirs(DIST_DIR, exist_ok=True)
    os.makedirs(os.path.join(DIST_DIR, "api"), exist_ok=True)

    # 1. Render index page
    index_html = render_index_page(items, config)
    with open(os.path.join(DIST_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    # 2. Render each error page
    for item in items:
        page_dir = os.path.join(DIST_DIR, "error", item["slug"])
        os.makedirs(page_dir, exist_ok=True)
        page_html = render_error_page(item, items, config)
        with open(os.path.join(page_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(page_html)

    # 3. Render sitemap.xml and robots.txt
    sitemap_xml = build_sitemap(items, config)
    with open(os.path.join(DIST_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    robots_txt = f"User-agent: *\nAllow: /\nSitemap: {config['site_url'].rstrip('/')}/sitemap.xml\n"
    with open(os.path.join(DIST_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots_txt)

    # 4. Export public JSON API endpoint (usable for RapidAPI / Apify / programmatic consumers)
    with open(os.path.join(DIST_DIR, "api", "errors.json"), "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"[OK] Sitio generado en {DIST_DIR}: {len(items)} páginas OEM + index.html + sitemap.xml + api/errors.json")


if __name__ == "__main__":
    main()
