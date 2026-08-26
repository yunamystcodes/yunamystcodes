import html
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

INDEX = Path("index.html")
HISTORY = Path("data/code_history.json")
CODE_RE = re.compile(r"\b[A-Z0-9]{8,24}\b")

# 20 independent/official/community endpoints. The collector deduplicates codes
# by their normalized value, so the same code found on many sources is rendered once.
SOURCES = [
    ("summonerswarcodes.us", "https://summonerswarcodes.us/", "table"),
    ("SWCoupon", "https://swcoupon.net/", "table"),
    ("SWQuery", "https://swquery.net/", "table"),
    ("SWGT", "https://swgt.io/gamecodes/", "table"),
    ("SWQ", "https://swq.jp/l/en-US/index.html", "table"),
    ("Pocket Gamer", "https://www.pocketgamer.com/summoners-war/codes/", "table"),
    ("Pocket Tactics", "https://www.pockettactics.com/summoners-war/codes", "table"),
    ("LevelGeeks", "https://levelgeeks.net/summoners-war-codes/", "page"),
    ("AllThingsHow", "https://allthings.how/summoners-war-codes/", "page"),
    ("Claude Gaming", "https://claude-gaming.com/summoners-war-codes/", "page"),
    ("eGamersWorld", "https://pt.egamersworld.com/blog/summoners-war-codes-this-date-QPcOSa2S5q", "page"),
    ("Try Hard Guides", "https://tryhardguides.com/summoners-war-codes-for-light-dark-mythic-scrolls/", "page"),
    ("Com2uS EN News", "https://www.summonerswar.com/en/skyarena/news/list", "official"),
    ("Com2uS PT News", "https://www.summonerswar.com/pt/skyarena/news/list", "official"),
    ("Com2uS FR News", "https://www.summonerswar.com/fr/skyarena/news/list", "official"),
    ("Hive Summoners War", "https://m.withhive.com/games/1321", "official"),
    ("Hive Global Notices", "https://www.withhive.com/notice/466/70082", "official"),
    ("Reddit r/summonerswar", "https://www.reddit.com/r/summonerswar/new/.json?limit=100", "reddit"),
    ("Reddit r/redeemgiftcodes", "https://www.reddit.com/r/redeemgiftcodes/new/.json?limit=100", "reddit"),
    ("Official Summoners War EU", "https://linktr.ee/summonerswar_eu", "official"),
]

KNOWN_REWARDS = {
    "INVOCATEUREU26": [("mana", "100,000"), ("mystic", "2")],
    "SWCTICKET2HAMBURG": [("mystic", "1")],
    "AUGSW2026V7N": [("energy", "100"), ("fire", "3")],
    "SWXFRIEREN2026": [("energy", "100"), ("mana", "300,000"), ("mystic", "3")],
    "AMPRELIMSLEGACYDRP": [("energy", "100"), ("mystic", "1")],
    "4READY4TDOT": [("mana", "200,000"), ("mystic", "1")],
    "LEGENDSWC2026HSL": [("energy", "100"), ("mystic", "1")],
    "YIQIZOUGUO10SWC": [("energy", "100"), ("mystic", "1")],
    "GLHF2026AMERICAS": [("mystic", "1")],
    "SWC26X10LEGACYBND": [("energy", "100"), ("mana", "200,000")],
    "PAI2026BANGKOK": [("mystic", "1")],
    "APAC26LEGASEA": [("mana", "200,000"), ("mystic", "1")],
}

STOPWORDS = {
    "SUMMONERS", "SUMMONERSWAR", "WAR", "CODES", "CODE", "ACTIVE", "PROMO",
    "REDEEM", "REWARDS", "NEW", "LATEST", "TODAY", "JULY", "AUGUST", "JUNE",
    "REDDIT", "SWGT", "SWQUERY", "QUERY", "HTTPS", "WITHHIVE", "ANDROID", "IOS",
}

ACTIVE_WORDS = ("active", "working", "valid", "currently working", "currently available", "ativo", "válido", "valido")
EXPIRED_WORDS = ("expired", "expirado", "invalid", "invalido", "inválido")

def clean(text):
    return re.sub(r"\s+", " ", html.unescape(text or "")).strip()

def normalise_code(value):
    value = re.sub(r"[^A-Z0-9]", "", value.upper())
    if not 8 <= len(value) <= 24 or value in STOPWORDS:
        return None
    if not any(c.isdigit() for c in value):
        return None
    return value

def extract_codes(text):
    found = []
    for raw in CODE_RE.findall(text.upper()):
        code = normalise_code(raw)
        if code and code not in found:
            found.append(code)
    return found

def fetch_html(url):
    response = requests.get(url, timeout=30, headers={"User-Agent": "YunaMystCodes/2.1 (+https://yunacodes.com/)"})
    response.raise_for_status()
    return response.text

def parse_table_source(name, url):
    soup = BeautifulSoup(fetch_html(url), "html.parser")
    found, expired = {}, set()
    for row in soup.select("tr"):
        cells = [clean(c.get_text(" ", strip=True)) for c in row.find_all(["td", "th"])]
        if not cells:
            continue
        row_text = " | ".join(cells).lower()
        status_active = any(x in row_text for x in ACTIVE_WORDS)
        status_expired = any(x in row_text for x in EXPIRED_WORDS)
        for code in dict.fromkeys(sum((extract_codes(cell) for cell in cells), [])):
            if status_expired and not status_active:
                expired.add(code)
            else:
                found[code] = {"code": code, "reward": cells[1] if len(cells) > 1 else "Recompensa não informada", "source": name}
    return found, expired

def parse_generic_page(name, url):
    soup = BeautifulSoup(fetch_html(url), "html.parser")
    text = clean(soup.get_text(" ", strip=True))
    found, expired = {}, set()
    # Generic code pages are treated conservatively: only codes appearing in a
    # nearby active/working context are accepted. Explicit expired contexts win.
    for raw in CODE_RE.findall(text.upper()):
        code = normalise_code(raw)
        if not code:
            continue
        pos = text.upper().find(raw)
        context = text[max(0, pos - 180):pos + 260].lower()
        if any(x in context for x in EXPIRED_WORDS) and not any(x in context for x in ACTIVE_WORDS):
            expired.add(code)
        elif any(x in context for x in ACTIVE_WORDS):
            found[code] = {"code": code, "reward": context, "source": name}
    return found, expired

def parse_reddit_source(name, url):
    response = requests.get(url, timeout=30, headers={"User-Agent": "YunaMystCodes/2.1 (+https://yunacodes.com/)"})
    response.raise_for_status()
    data = response.json()
    found = {}
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    for child in data.get("data", {}).get("children", []):
        post = child.get("data", {})
        created = datetime.fromtimestamp(post.get("created_utc", 0), tz=timezone.utc)
        if created < cutoff:
            continue
        body = " ".join([post.get("title", ""), post.get("selftext", "")])
        for code in extract_codes(body):
            found[code] = {"code": code, "reward": "Recompensa não informada", "source": name}
    return found, set()

def parse_source(name, url, kind):
    if kind == "table":
        return parse_table_source(name, url)
    if kind == "reddit":
        return parse_reddit_source(name, url)
    return parse_generic_page(name, url)

def collect_sources():
    merged, explicitly_expired = {}, set()
    successful, errors = 0, []
    for name, url, kind in SOURCES:
        try:
            found, expired = parse_source(name, url, kind)
            successful += 1
            explicitly_expired.update(expired)
            for code, item in found.items():
                if code not in merged:
                    merged[code] = item
                else:
                    if merged[code]["reward"] == "Recompensa não informada" and item["reward"] != "Recompensa não informada":
                        merged[code]["reward"] = item["reward"]
                    merged[code]["source"] += ", " + item["source"]
    except Exception as exc:
            errors.append(f"{name}: {exc}")
    # A source saying expired cannot override another source saying active.
    explicitly_expired.difference_update(merged.keys())
    if successful < 5:
        raise RuntimeError("Poucas fontes responderam: " + " | ".join(errors))
    return merged, explicitly_expired, successful, errors

def load_history():
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY.exists():
        return {}
    try:
        return json.loads(HISTORY.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_history(history):
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def reward_items(code, reward):
    if code in KNOWN_REWARDS:
        return KNOWN_REWARDS[code]
    text = clean(reward).lower()
    patterns = [("mystic", r"mystic(?:al)?\s*scroll|mystical|pergaminho\s*m[íi]stico"),("fire", r"fire\s*scroll|scroll\s*fire|pergaminho\s*de\s*fogo"),("water", r"water\s*scroll|scroll\s*water|pergaminho\s*de\s*[aá]gua"),("wind", r"wind\s*scroll|scroll\s*wind|pergaminho\s*de\s*vento"),("mana", r"mana"),("crystal", r"crystal|crystals|cristal|cristais"),("energy", r"energy|energia")]
    items = []
    for kind, pattern in patterns:
        m = re.search(rf"(\d[\d,.]*)\s*(?:x|×)?\s*(?:\+)?\s*(?:{pattern})", text) or re.search(rf"(?:{pattern})\s*(?:x|×)?\s*(\d[\d,.]*)", text)
        if m:
            items.append((kind, m.group(1).rstrip(",.")))
    return items

def reward_html(code, reward):
    items = reward_items(code, reward)
    if not items:
        return '<span class="reward-chip"><span class="reward-unknown">🎁</span><b>Recompensa do código</b></span>'
    out = []
    for kind, qty in items:
        icon = '<span class="reward-energy">⚡</span>' if kind == "energy" else f'<span class="reward-img reward-{kind}"></span>'
        out.append(f'<span class="reward-chip" title="{html.escape(kind)}">{icon}<b>×{html.escape(qty)}</b></span>')
    return "".join(out)

def card(item, expired=False):
    code = html.escape(item["code"])
    rewards = reward_html(item["code"], item.get("reward", ""))
    expired_class = " expired" if expired else ""
    buttons = "" if expired else (f'<button class="copy" onclick="copiarCodigo(\'{code}\',this)"><span data-i18n="copy">▣ COPIAR</span></button>' f'<a class="iphone" href="https://withhive.me/313/{code}" target="_blank" rel="noopener"><span class="iphone-full"> LINK IPHONE</span><span class="iphone-short"> LINK</span></a>')
    return f'<article class="code{expired_class}" data-code="{code}"><div class="gift">🎁</div><div class="cinfo"><strong>{code}</strong><small>{"Código expirado" if expired else "Atualizado automaticamente"}</small></div><div class="reward-icons" aria-label="Recompensas">{rewards}</div>{buttons}</article>'

def update_index(active_items, expired_items):
    soup = BeautifulSoup(INDEX.read_text(encoding="utf-8"), "html.parser")
    active = soup.find(id="activeCodesList")
    if active is None:
        raise RuntimeError("Bloco activeCodesList não encontrado.")
    active.clear()
    for item in active_items:
        active.append(BeautifulSoup(card(item), "html.parser"))
    expired_panel = soup.find(class_="expired-panel")
    if expired_panel is not None:
        expired_panel.clear()
        if expired_items:
            for item in expired_items:
                expired_panel.append(BeautifulSoup(card(item, expired=True), "html.parser"))
        else:
            empty = soup.new_tag("div", attrs={"class": "expired-empty"})
            empty.string = "Nenhum código expirado registrado."
            expired_panel.append(empty)
    INDEX.write_text(str(soup), encoding="utf-8")

def main():
    merged, explicitly_expired, successful, errors = collect_sources()
    now = datetime.now(timezone.utc)
    history = load_history()
    active_codes = set(merged)
    for code, item in merged.items():
        record = history.get(code, {})
        record.update({"code": code, "reward": item.get("reward", record.get("reward", "Recompensa não informada")), "sources": sorted(set(record.get("sources", []) + [s.strip() for s in item.get("source", "").split(",") if s.strip()])), "last_seen": now.isoformat(), "missing_runs": 0, "status": "active"})
        history[code] = record
    for code, record in list(history.items()):
        if code in active_codes:
            continue
        if code in explicitly_expired:
            record["status"] = "expired"
            record["expired_at"] = now.isoformat()
            history[code] = record
            continue
        if record.get("status") == "expired":
            continue
        record["missing_runs"] = int(record.get("missing_runs", 0)) + 1
        record["status"] = "active" if record["missing_runs"] < 2 else "expired"
        if record["status"] == "expired":
            record["expired_at"] = now.isoformat()
        history[code] = record
    save_history(history)
    active_items = sorted([v for v in history.values() if v.get("status") == "active"], key=lambda x: x.get("last_seen", ""), reverse=True)
    expired_items = sorted([v for v in history.values() if v.get("status") == "expired"], key=lambda x: x.get("last_seen", ""), reverse=True)
    update_index(active_items, expired_items)
    print(f"Fontes OK: {successful}/{len(SOURCES)}")
    print("Códigos ativos únicos:", ", ".join(x["code"] for x in active_items))
    print("Códigos expirados arquivados:", len(expired_items))
    if errors:
        print("Avisos:", " | ".join(errors))

if __name__ == "__main__":
    main()
