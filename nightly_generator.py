#!/usr/bin/env python3
"""
Nightly Autonomous Worker — AveríasOEM
Se ejecuta cada madrugada:
1. Extrae nuevas fichas de la cola verificada (data/expansion_queue.json) o genera nuevas vía Gemini API si GEMINI_API_KEY está configurada.
2. Las añade a data/errors_db.json sin duplicados.
3. Reconstruye todo el sitio estático SEO (dist/), sitemap.xml y feed JSON.
4. Si hay un repositorio remoto configurado en Git, hace commit y push automático para desplegar en GitHub Pages / Cloudflare Pages.
"""

import json
import os
import subprocess
import urllib.request
from datetime import datetime

import build_site

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
DB_PATH = os.path.join(BASE_DIR, "data", "errors_db.json")
QUEUE_PATH = os.path.join(BASE_DIR, "data", "expansion_queue.json")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "nightly.log")


def log(msg):
    os.makedirs(LOG_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_via_gemini_api(existing_ids, count=2):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return []

    prompt = (
        f"Genera un array JSON con {count} códigos de avería reales y muy buscados de electrodomésticos, "
        f"calderas, cafeteras, impresoras 3D o patinetes eléctricos en España/Latinoamérica que NO estén en esta lista de IDs: "
        f"{', '.join(list(existing_ids)[-30:])}. "
        "Para cada uno incluye EXACTAMENTE estas claves: "
        "id, slug, category, brands (array), error_code, popular_models (array), symptom, technical_cause, "
        "oem_part_name, oem_part_number (código OEM real del fabricante), secondary_part_number, "
        "affiliate_search_query, part_price_range (en €), technician_cost_estimate (en €), "
        "repair_time_minutes (int), difficulty, diagnostic_steps (array de 3-4 strings), "
        "faq (array de objetos con 'q' y 'a'). Responde SOLO con el JSON válido."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            raw_text = body["candidates"][0]["content"]["parts"][0]["text"]
            new_items = json.loads(raw_text)
            if isinstance(new_items, list):
                log(f"Gemini API generó {len(new_items)} nuevas fichas OEM.")
                return new_items
    except Exception as e:
        log(f"Aviso Gemini API (usando cola local verificada): {e}")
    return []


def auto_git_commit_and_push(added_count):
    try:
        subprocess.run(["git", "add", "data/", "dist/"], cwd=BASE_DIR, check=True)
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if not status:
            log("Git: Sin cambios pendientes para commit.")
            return

        msg = f"chore(nightly): +{added_count} nuevas fichas OEM autogeneradas ({datetime.now().strftime('%Y-%m-%d')})"
        subprocess.run(["git", "commit", "-m", msg], cwd=BASE_DIR, check=True)
        log(f"Git commit creado: {msg}")

        remotes = subprocess.run(
            ["git", "remote"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if "origin" in remotes.splitlines():
            subprocess.run(["git", "push", "origin", "HEAD"], cwd=BASE_DIR, check=True)
            log("Git push completado a origin.")
        else:
            log("Git commit local guardado (añade 'git remote add origin <URL>' para auto-despliegue en la nube).")
    except Exception as e:
        log(f"Aviso en paso Git: {e}")


def main():
    config = load_json(CONFIG_PATH, {})
    db = load_json(DB_PATH, [])
    queue = load_json(QUEUE_PATH, [])

    existing_ids = {item["id"] for item in db}
    existing_slugs = {item["slug"] for item in db}
    items_per_night = config.get("nightly_settings", {}).get("items_per_night", 3)
    today = datetime.now().strftime("%Y-%m-%d")

    added = []

    # 1. Extraer de la cola verificada
    remaining_queue = []
    for item in queue:
        if len(added) < items_per_night and item["id"] not in existing_ids and item["slug"] not in existing_slugs:
            item["created_at"] = today
            db.append(item)
            existing_ids.add(item["id"])
            existing_slugs.add(item["slug"])
            added.append(item["id"])
        else:
            remaining_queue.append(item)

    # 2. Si faltan fichas para completar la cuota nocturna, intentar vía Gemini API
    if len(added) < items_per_night:
        needed = items_per_night - len(added)
        ai_items = generate_via_gemini_api(existing_ids, count=needed)
        for item in ai_items:
            if isinstance(item, dict) and item.get("id") and item.get("slug"):
                if item["id"] not in existing_ids and item["slug"] not in existing_slugs:
                    item["created_at"] = today
                    db.append(item)
                    existing_ids.add(item["id"])
                    existing_slugs.add(item["slug"])
                    added.append(item["id"])

    save_json(DB_PATH, db)
    save_json(QUEUE_PATH, remaining_queue)

    # 3. Reconstruir el sitio estático y sitemap
    build_site.main()

    log(f"Ejecución nocturna completada. Añadidas {len(added)} fichas nuevas: {added}. Total en DB: {len(db)}. Cola restante: {len(remaining_queue)}.")

    # 4. Auto-commit & push si está habilitado
    if config.get("nightly_settings", {}).get("auto_git_push", True):
        auto_git_commit_and_push(len(added))


if __name__ == "__main__":
    main()
