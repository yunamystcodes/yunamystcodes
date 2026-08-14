import html
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://summonerswarcodes.us/"
INDEX = Path("index.html")
CODE_RE = re.compile(r"\b[A-Z0-9]{8,24}\b")

EXTRA_CODES = {
    "SWCTICKET2HAMBURG": "1 Mystical Scroll",
    "INVOCATEUREU26": "100,000 Mana + 2 Mystical Scrolls",
}

# Recompensas conhecidas para os códigos que aparecem atualmente no site.
REWARD_ITEMS = {
    "INVOCATEUREU26": [("mana", "🔵", "100,000"), ("mystic", "📜", "2")],
    "SWCTICKET2HAMBURG": [("mystic", "📜", "1")],
    "AUGSW2026V7N": [("energy", "⚡", "100"), ("fire", "🔥", "1")],
    "SWXFRIEREN2026": [("energy", "⚡", "100"), ("mana", "🔵", "300,000"), ("mystic", "📜", "3")],
}


def clean(text):
    return re.sub(r"\s+", " ", html.unescape(text or "")).strip()


def fetch_codes():
    response = requests.get(
        SOURCE_URL,
        timeout=30,
        headers={"User-Agent": "YunaMystCodes/1.0 (+https://yunamystcodes.github.io/yunamystcodes/)"},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    found = []
    seen = set()

    for row in soup.select("tr"):
        cells = [clean(c.get_text(" ", strip=True)) for c in row.find_all(["td", "th"])]
        if not cells:
            continue
        joined = " | ".join(cells)
        if "active" not in joined.lower():
            continue
        match = None
        for cell in cells:
            match = CODE_RE.search(cell.upper())
            if match:
                break
        if not match:
            continue
        code = match.group(0).upper()
        if code in seen:
            continue
        seen.add(code)
        reward = cells[1] if len(cells) > 1 else "Recompensas não informadas"
        found.append({"code": code, "reward": reward[:180]})

    for code, reward in EXTRA_CODES.items():
        if code not in seen:
            found.insert(0, {"code": code, "reward": reward})
            seen.add(code)

    if not found:
        raise RuntimeError("Nenhum código ativo foi encontrado na fonte.")
    return found


def parse_reward_items(reward):
    text = clean(reward).lower()
    patterns = [
        ("mystic", r"(?:scroll\s*)?mystical|mystic(?:al)?\s*scroll|pergaminho\s*m[íi]stico|scroll\s*mystical", "📜"),
        ("fire", r"fire\s*scroll|scroll\s*fire|pergaminho\s*de\s*fogo", "🔥"),
        ("water", r"water\s*scroll|scroll\s*water|pergaminho\s*de\s*[aá]gua", "💧"),
        ("wind", r"wind\s*scroll|scroll\s*wind|pergaminho\s*de\s*vento", "🍃"),
        ("mana", r"mana", "🔵"),
        ("crystal", r"crystal|crystals|cristal|cristais", "💎"),
        ("energy", r"energy|energia", "⚡"),
    ]
    items = []
    for kind, pattern, icon in patterns:
        grouped = rf"(?:{pattern})"
        before = re.search(rf"(\d[\d,.]*)\s*(?:x|×)?\s*(?:\+)?\s*{grouped}", text)
        after = re.search(rf"{grouped}\s*(?:x|×)?\s*(\d[\d,.]*)", text)
        match = before or after
        if match and match.group(1):
            qty = match.group(1).rstrip(",.")
            items.append((kind, icon, qty))
    return items


def reward_icons(code, reward):
    items = REWARD_ITEMS.get(code) or parse_reward_items(reward or "")
    if not items:
        return '<span class="reward-unknown">?</span>'
    return "".join(
        f'<span class="reward-chip {kind}" title="{html.escape(kind)}">'
        f'<span class="reward-icon">{icon}</span><b>×{qty}</b></span>'
        for kind, icon, qty in items
    )


def card(item):
    code = html.escape(item["code"])
    rewards = reward_icons(item["code"], item["reward"] or "")
    return (
        f'<article class="code" data-code="{code}">'
        f'<div class="gift">🎁</div>'
        f'<div class="cinfo"><strong>{code}</strong><small>🔄 Atualizado automaticamente</small></div>'
        f'<div class="reward-icons" aria-label="Recompensas">{rewards}</div>'
        f'<button class="copy" onclick="copiarCodigo(\'{code}\',this)"><span data-i18n="copy">▣ COPIAR</span></button>'
        f'<a class="iphone" href="https://withhive.me/313/{code}" target="_blank" rel="noopener">'
        f'<span class="iphone-full"> LINK IPHONE</span><span class="iphone-short"> LINK</span></a></article>'
    )


STYLE_PATCH = '''
/* Recompensas: apenas símbolo + quantidade */
.reward-summary{display:none!important}
.reward-icons{grid-column:3 / 6;display:flex;align-items:center;justify-content:center;gap:12px;min-width:0;flex-wrap:wrap}.reward-chip{display:inline-flex;align-items:center;gap:4px;white-space:nowrap}.reward-icon{font-size:24px;line-height:1;filter:drop-shadow(0 0 4px rgba(255,255,255,.18))}.reward-chip b{font-size:12px;color:#fff}.reward-unknown{color:#aaa;font-size:12px}
@media(max-width:1050px){.reward-icons{grid-column:3 / 5;gap:9px}.reward-icon{font-size:22px}}
@media(max-width:850px){.reward-icons{grid-column:1 / 3;grid-row:2;justify-content:flex-start;gap:10px;padding-top:2px}.reward-icon{font-size:22px}.reward-chip b{font-size:11px}}
@media(max-width:600px){.reward-icons{grid-column:1 / 3;grid-row:2;justify-content:flex-start;gap:10px}.reward-icon{font-size:21px}.reward-chip b{font-size:11px}.code .copy{grid-row:3}.code .iphone{grid-row:3}}
'''


def update_index(codes):
    text = INDEX.read_text(encoding="utf-8")
    text = re.sub(r'\n/\* Ajustes de leitura dos códigos e recompensas \*/.*?(?=\n</style>)', '', text, flags=re.S)
    text = re.sub(r'\n/\* Recompensas: apenas símbolo \+ quantidade \*/.*?(?=\n</style>)', '', text, flags=re.S)
    text = text.replace('</style>', STYLE_PATCH + '</style>', 1)

    marker = '<div class="codes" id="activeCodesList">'
    start = text.find(marker)
    if start == -1:
        raise RuntimeError('Bloco da lista de códigos ativos não encontrado.')
    content_start = start + len(marker)
    end = text.find('</div>\n<div class="more"', content_start)
    if end == -1:
        end = text.find('</div><div class="more"', content_start)
    if end == -1:
        raise RuntimeError('Fim da lista de códigos ativos não encontrado.')

    cards = "\n".join(card(item) for item in codes)
    new_text = text[:content_start] + "\n" + cards + "\n" + text[end:]
    INDEX.write_text(new_text, encoding="utf-8")


if __name__ == "__main__":
    codes = fetch_codes()
    update_index(codes)
    print(f"Atualizados {len(codes)} códigos ativos.")
