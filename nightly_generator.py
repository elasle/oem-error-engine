#!/usr/bin/env python3
"""
Nightly Autonomous Worker — OEMPartDecoder / AveríasOEM (Bilingual en-US + es-US)
Every night:
1. Promotes new verified US-English OEM error entries from data/expansion_queue_en.json -> data/errors_en_db.json
2. Promotes new verified Spanish OEM error entries from data/expansion_queue.json -> data/errors_db.json
3. Rebuilds the entire static SEO portal (dist/), sitemap.xml, llms.txt, and JSON API.
4. Commits and pushes to GitHub (auto-deploying to GitHub Pages).
5. Pings IndexNow (api.indexnow.org) so Bing, DuckDuckGo, Yahoo & ChatGPT Search index new pages immediately.
"""

import json
import os
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime

import build_site

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
EN_DB_PATH = os.path.join(BASE_DIR, "data", "errors_en_db.json")
EN_QUEUE_PATH = os.path.join(BASE_DIR, "data", "expansion_queue_en.json")
ES_DB_PATH = os.path.join(BASE_DIR, "data", "errors_db.json")
ES_QUEUE_PATH = os.path.join(BASE_DIR, "data", "expansion_queue.json")
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


def promote_from_queue(db_path, queue_path, limit, lang):
    db = load_json(db_path, [])
    queue = load_json(queue_path, [])
    existing_ids = {item["id"] for item in db}
    existing_slugs = {item["slug"] for item in db}
    today = datetime.now().strftime("%Y-%m-%d")

    added_slugs = []
    remaining = []
    for item in queue:
        if len(added_slugs) < limit and item["id"] not in existing_ids and item["slug"] not in existing_slugs:
            item["created_at"] = today
            item["lang"] = lang
            db.append(item)
            existing_ids.add(item["id"])
            existing_slugs.add(item["slug"])
            added_slugs.append(item["slug"])
        else:
            remaining.append(item)

    save_json(db_path, db)
    save_json(queue_path, remaining)
    return added_slugs, len(db), len(remaining)


def ping_indexnow(config, slugs):
    base_url = config.get("site_url", "https://elasle.github.io/oem-error-engine").rstrip("/")
    parsed = urllib.parse.urlparse(base_url)
    host = parsed.netloc
    key = build_site.INDEXNOW_KEY
    key_location = f"{base_url}/{key}.txt"

    url_list = [f"{base_url}/", f"{base_url}/es/", f"{base_url}/sitemap.xml", f"{base_url}/llms.txt"]
    for s in slugs:
        url_list.append(f"{base_url}/error/{s}/")

    payload = {
        "host": host,
        "key": key,
        "keyLocation": key_location,
        "urlList": url_list[:100],
    }
    try:
        req = urllib.request.Request(
            "https://api.indexnow.org/indexnow",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            log(f"IndexNow ping sent for {len(url_list)} URLs -> HTTP {resp.status}")
    except Exception as e:
        log(f"IndexNow ping notice: {e}")


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
            log("Git: No pending changes to commit.")
            return

        msg = f"chore(nightly): +{added_count} new bilingual OEM pages ({datetime.now().strftime('%Y-%m-%d')})"
        subprocess.run(["git", "commit", "-m", msg], cwd=BASE_DIR, check=True)
        log(f"Git commit created: {msg}")

        remotes = subprocess.run(
            ["git", "remote"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if "origin" in remotes.splitlines():
            subprocess.run(["git", "push", "origin", "HEAD"], cwd=BASE_DIR, check=True)
            log("Git push completed to origin.")
    except Exception as e:
        log(f"Git notice: {e}")


def main():
    config = load_json(CONFIG_PATH, {})
    items_per_night = config.get("nightly_settings", {}).get("items_per_night", 2)

    en_added, en_total, en_q_left = promote_from_queue(EN_DB_PATH, EN_QUEUE_PATH, items_per_night, "en")
    es_added, es_total, es_q_left = promote_from_queue(ES_DB_PATH, ES_QUEUE_PATH, items_per_night, "es")

    build_site.main()

    all_added = en_added + es_added
    log(
        f"Nightly run complete: +{len(en_added)} EN (total {en_total}, queue {en_q_left}), "
        f"+{len(es_added)} ES (total {es_total}, queue {es_q_left})."
    )

    if config.get("nightly_settings", {}).get("auto_git_push", True):
        auto_git_commit_and_push(len(all_added))

    if config.get("nightly_settings", {}).get("ping_search_engines", True):
        # Ping IndexNow with all active slugs
        all_en = [x["slug"] for x in load_json(EN_DB_PATH, [])]
        all_es = [x["slug"] for x in load_json(ES_DB_PATH, [])]
        ping_indexnow(config, all_en + all_es)


if __name__ == "__main__":
    main()
