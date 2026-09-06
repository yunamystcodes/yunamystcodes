import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

INDEX = Path("index.html")
HISTORY = Path("data/code_history.json")
CODE_RE = re.compile(r"\b[A-Z0-9]{8,24}\b")

# Only structured/live code tables are trusted for the ACTIVE list.
# Long guide pages are deliberately excluded because they often contain
# historical/expired codes in the same article.
SOURCES = [
    ("SWQuery", "https://swquery.net/"),
    ("SWGT", "https://swgt.io/gamecodes/"),
    ("summonerswarcodes.us", "https://summonerswarcodes.us/"),
    ("SWCoupon", "https://swcoupon.net/"),
    ("SWQ", "https://swq.jp/l/en-US/index.html"),
]

KNOWN_REWARDS = {
    "SEPSW2026I8B": [("mana", "300,000"), ("water", "3")],
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
    "REDEEM", "REWARDS", "NEW", "LATEST", "TODAY", "HTTPS", "WITHHIVE",
    "ANDROID", "IOS", "QUERY", "SWGT", "SWQ", "SWCOUPON",
}

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


def fetch(url):
    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": "YunaMystCodes/3.0 (+https://yunacodes.com/)"},
    )
    response.raise_for_status()
    return response.text


def parse_table_source(name, url):
    soup = BeautifulSoup(fetch(url), "html.parser")
    found = {}
    expired = set()

    for row in soup.select("tr"):
        cells = [clean(c.get_text(" ", strip=True)) for c in row.find_all(["td", "th"])]
        if not cells:
            continue
        row_text = " | ".join(cells)
        lower = row_text.lower()
        codes = []
        for cell in cells:
            codes.extend(extract_codes(cell))

        for code in dict.fromkeys(codes):
            if any(word in lower for word in EXPIRED_WORDS):
                expired.add(code)
                continue
            reward = " | ".join(cells[1:]) if len(cells) > 1 else "Recompensa não informada"
            found[code] = {
                "code": code,
                "reward": reward,
                "source": name,
            }
    return found, expired


def collect_sources():
    merged = {}
    explicitly_expired = set()
    successful = 0
    errors = []

    for name, url in SOURCES:
        try:
            found, expired = parse_table_source(name, url)
            successful += 1
            explicitly_expired.update(expired)
            for code, item in found.items():
                if code not in merged:
                    merged[code] = item
                else:
                    old = merged[code]
                    if old["reward"] == "Recompensa não informada" and item["reward"] != "Recompensa não informada":
                        old["reward"] = item["reward"]
                    old["source"] += ", " + item["source"]
        except Exception as exc:
            errors.append(f"{name}: {exc}")

    explicitly_expired.difference_update(merged.keys())
    if successful < 2:
        raise RuntimeError(
            "Fontes confiáveis insuficientes para substituir a lista: "
            + str(successful)
            + ". "
            + " | ".join(errors)
        )
    return merged, explicitly_expired, successful, errors


def load_history():
    if not HISTORY.exists():
        return {}
    try:
        return json.loads(HISTORY.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_history(history):
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(
        json.dumps(history, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def reward_items(code, reward):
    if code in KNOWN_REWARDS:
        return KNOWN_REWARDS[code]
    text = clean(reward).lower()
    patterns = [
        ("mystic", r"mystic(?:al)?\s*scroll|mystical|pergaminho\s*m[íi]stico"),
        ("fire", r"fire\s*scroll|scroll\s*fire|pergaminho\s*de\s*fogo"),
        ("water", r"water\s*scroll|scroll\s*water|pergaminho\s*de\s*[aá]gua"),
        ("wind", r"wind\s*scroll|scroll\s*wind|pergaminho\s*de\s*vento"),
        ("mana", r"mana"),
        ("crystal", r"crystal|crystals|cristal|cristais"),
        ("energy", r"energy|energia"),
    ]
    items = []
    for kind, pattern in patterns:
        m = re.search(rf"(\d[\d,.]*)\s*(?:x|×)?\s*(?:\+)?\s*(?:{pattern})", text)
        if not m:
            m = re.search(rf"(?:{pattern})\s*(?:x|×)?\s*(\d[\d,.]*)", text)
        if m:
            items.append((kind, m.group(1).rstrip(",.")))
    return items


def reward_html(code, reward):
    items = reward_items(code, reward)
    if not items:
        return '<span class="reward-chip"><span class="reward-unknown">🎁</span><b>Recompensa</b></span>'
    out = []
    for kind, qty in items:
        icon = '<span class="reward-energy">⚡</span>' if kind == "energy" else f'<span class="reward-img reward-{kind}"></span>'
        out.append(f'<span class="reward-chip" title="{html.escape(kind)}">{icon}<b>×{html.escape(qty)}</b></span>')
    return "".join(out)


def card(item, expired=False):
    code = html.escape(item["code"])
    rewards = reward_html(item["code"], item.get("reward", ""))
    expired_class = " expired" if expired else ""
    if expired:
        buttons = ""
    else:
        buttons = (
            f'<button class="copy" onclick="copiarCodigo(\'{code}\',this)">'
            '<span data-i18n="copy">▣ COPIAR</span></button>'
            f'<a class="iphone" href="https://withhive.me/313/{code}" target="_blank" rel="noopener">'
            '<span class="iphone-full"> LINK IPHONE</span><span class="iphone-short"> LINK</span></a>'
        )
    label = "Código expirado" if expired else "Atualizado automaticamente"
    return (
        f'<article class="code{expired_class}" data-code="{code}">'
        f'<div class="gift">🎁</div><div class="cinfo"><strong>{code}</strong><small>{label}</small></div>'
        f'<div class="reward-icons" aria-label="Recompensas">{rewards}</div>{buttons}</article>'
    )


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
        for item in expired_items:
            expired_panel.append(BeautifulSoup(card(item, expired=True), "html.parser"))

    INDEX.write_text(str(soup), encoding="utf-8")


def main():
    merged, explicitly_expired, successful, errors = collect_sources()
    now = datetime.now(timezone.utc)
    history = load_history()
    active_codes = set(merged)

    # Existing codes are updated only from trusted structured sources.
    for code, item in merged.items():
        record = history.get(code, {})
        if record.get("status") == "expired" or record.get("expired_at"):
            continue
        previous_sources = record.get("sources", [])
        current_sources = [s.strip() for s in item.get("source", "").split(",") if s.strip()]
        record.update(
            {
                "code": code,
                "reward": item.get("reward", record.get("reward", "Recompensa não informada")),
                "sources": sorted(set(previous_sources + current_sources)),
                "last_seen": now.isoformat(),
                "missing_runs": 0,
                "status": "active",
            }
        )
        history[code] = record

    # With at least two trusted sources responding, anything previously active
    # but absent from ALL trusted live tables is expired immediately. This is
    # what prevents old 2025/2026 event codes from remaining on the site.
    for code, record in list(history.items()):
        if code in explicitly_expired:
            record["status"] = "expired"
            record["expired_at"] = record.get("expired_at", now.isoformat())
            history[code] = record
            continue
        if record.get("status") != "active" or code in active_codes:
            continue
        record["status"] = "expired"
        record["expired_at"] = record.get("expired_at", now.isoformat())
        record["missing_runs"] = int(record.get("missing_runs", 0)) + 1
        history[code] = record

    save_history(history)

    active_items = sorted(
        [v for v in history.values() if v.get("status") == "active" and v.get("code") in active_codes],
        key=lambda x: x.get("last_seen", ""),
        reverse=True,
    )
    expired_items = sorted(
        [v for v in history.values() if v.get("status") == "expired"],
        key=lambda x: x.get("expired_at", x.get("last_seen", "")),
        reverse=True,
    )

    update_index(active_items, expired_items)
    print(f"Fontes confiáveis OK: {successful}/{len(SOURCES)}")
    print(f"Códigos ativos publicados: {len(active_items)}")
    print("Ativos:", ", ".join(x["code"] for x in active_items))
    print(f"Códigos antigos removidos da lista ativa: {len(expired_items)}")
    if errors:
        print("Fontes indisponíveis:")
        for error in errors:
            print(" -", error)


if __name__ == "__main__":
    main()
