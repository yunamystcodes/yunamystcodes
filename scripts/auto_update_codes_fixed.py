import html
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://summonerswarcodes.us/"
INDEX = Path("index.html")
CODE_RE = re.compile(r"\b[A-Z0-9]{8,24}\b")
FALLBACK_CODES = {"HURRASWC2026": "Recompensas não informadas"}
KNOWN_REWARDS = {
    "INVOCATEUREU26": [("mana", "100,000"), ("mystic", "2")],
    "SWCTICKET2HAMBURG": [("mystic", "1")],
    "AUGSW2026V7N": [("energy", "100"), ("fire", "1")],
    "SWXFRIEREN2026": [("energy", "100"), ("mana", "300,000"), ("mystic", "3")],
}


def clean(text):
    return re.sub(r"\s+", " ", html.unescape(text or "")).strip()


def fetch_codes():
    response = requests.get(SOURCE_URL, timeout=30, headers={"User-Agent": "YunaMystCodes/1.0 (+https://yunacodes.com/)"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    found, seen = [], set()
    for row in soup.select("tr"):
        cells = [clean(c.get_text(" ", strip=True)) for c in row.find_all(["td", "th"])]
        if not cells or not ("active" in " | ".join(cells).lower() or "ativo" in " | ".join(cells).lower()):
            continue
        match = next((CODE_RE.search(cell.upper()) for cell in cells if CODE_RE.search(cell.upper())), None)
        if not match:
            continue
        code = match.group(0).upper()
        if code in seen:
            continue
        seen.add(code)
        reward = cells[1] if len(cells) > 1 else "Recompensas não informadas"
        found.append({"code": code, "reward": reward[:180]})
    for code, reward in FALLBACK_CODES.items():
        if code not in seen:
            found.insert(0, {"code": code, "reward": reward})
    if not found:
        raise RuntimeError("Nenhum código ativo encontrado na fonte.")
    return found


def reward_items(code, reward):
    if code in KNOWN_REWARDS:
        return KNOWN_REWARDS[code]
    text = clean(reward).lower()
    patterns = [
        ("mystic", r"mystic(?:al)?\s*scroll|mystical|pergaminho\s*m[íi]stico"),
        ("fire", r"fire\s*scroll|scroll\s*fire|pergaminho\s*de\s*fogo"),
        ("water", r"water\s*scroll|scroll\s*water|pergaminho\s*de\s*[aá]gua"),
        ("wind", r"wind\s*scroll|scroll\s*wind|pergaminho\s*de\s*vento"),
        ("mana", r"mana"), ("crystal", r"crystal|crystals|cristal|cristais"),
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
        return '<span class="reward-chip"><span class="reward-unknown">🎁</span><b>Recompensa do código</b></span>'
    out = []
    for kind, qty in items:
        icon = '<span class="reward-energy">⚡</span>' if kind == "energy" else f'<span class="reward-img reward-{kind}"></span>'
        out.append(f'<span class="reward-chip" title="{html.escape(kind)}">{icon}<b>×{html.escape(qty)}</b></span>')
    return "".join(out)


def card(item):
    code = html.escape(item["code"])
    rewards = reward_html(item["code"], item["reward"])
    return (
        f'<article class="code" data-code="{code}"><div class="gift">🎁</div>'
        f'<div class="cinfo"><strong>{code}</strong><small>🔄 Atualizado automaticamente</small></div>'
        f'<div class="reward-icons" aria-label="Recompensas">{rewards}</div>'
        f'<button class="copy" onclick="copiarCodigo(\'{code}\',this)"><span data-i18n="copy">▣ COPIAR</span></button>'
        f'<a class="iphone" href="https://withhive.me/313/{code}" target="_blank" rel="noopener">'
        f'<span class="iphone-full"> LINK IPHONE</span><span class="iphone-short"> LINK</span></a></article>'
    )


def update_index(codes):
    text = INDEX.read_text(encoding="utf-8")
    marker = '<div class="codes" id="activeCodesList">'
    start = text.find(marker)
    if start == -1:
        raise RuntimeError("Bloco da lista de códigos ativos não encontrado.")
    content_start = start + len(marker)
    section = re.search(r'<div[^>]*class="[^"]*(?:expired-tab|more)[^"]*"', text[content_start:], re.I)
    if not section:
        raise RuntimeError("Secção de códigos expirados não encontrada.")
    section_start = content_start + section.start()
    end = text.rfind('</div>', content_start, section_start)
    if end == -1:
        raise RuntimeError("Fim da lista de códigos ativos não encontrado.")
    end += len('</div>')
    cards = "\n".join(card(item) for item in codes)
    INDEX.write_text(text[:content_start] + "\n" + cards + "\n" + text[end:], encoding="utf-8")


if __name__ == "__main__":
    codes = fetch_codes()
    update_index(codes)
    print("Códigos ativos atualizados:", ", ".join(x["code"] for x in codes))
