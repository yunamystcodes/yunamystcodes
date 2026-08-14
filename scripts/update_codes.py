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

# Sprite criado a partir exatamente das seis imagens enviadas pelo utilizador:
# mystic, fire, water, wind, mana e crystal.
REWARD_SPRITE = "data:image/png;base64,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"

REWARD_ITEMS = {
    "INVOCATEUREU26": [("mana", "100,000"), ("mystic", "2")],
    "SWCTICKET2HAMBURG": [("mystic", "1")],
    "AUGSW2026V7N": [("energy", "100"), ("fire", "1")],
    "SWXFRIEREN2026": [("energy", "100"), ("mana", "300,000"), ("mystic", "3")],
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
        ("mystic", r"(?:scroll\s*)?mystical|mystic(?:al)?\s*scroll|pergaminho\s*m[íi]stico|scroll\s*mystical"),
        ("fire", r"fire\s*scroll|scroll\s*fire|pergaminho\s*de\s*fogo"),
        ("water", r"water\s*scroll|scroll\s*water|pergaminho\s*de\s*[aá]gua"),
        ("wind", r"wind\s*scroll|scroll\s*wind|pergaminho\s*de\s*vento"),
        ("mana", r"mana"),
        ("crystal", r"crystal|crystals|cristal|cristais"),
        ("energy", r"energy|energia"),
    ]
    items = []
    for kind, pattern in patterns:
        grouped = rf"(?:{pattern})"
        before = re.search(rf"(\d[\d,.]*)\s*(?:x|×)?\s*(?:\+)?\s*{grouped}", text)
        after = re.search(rf"{grouped}\s*(?:x|×)?\s*(\d[\d,.]*)", text)
        match = before or after
        if match and match.group(1):
            items.append((kind, match.group(1).rstrip(",.")))
    return items


def reward_icons(code, reward):
    items = REWARD_ITEMS.get(code) or parse_reward_items(reward or "")
    if not items:
        return '<span class="reward-unknown">?</span>'
    html_items = []
    for kind, qty in items:
        if kind == "energy":
            icon = '<span class="reward-energy">⚡</span>'
        else:
            icon = f'<span class="reward-img reward-{kind}"></span>'
        html_items.append(
            f'<span class="reward-chip" title="{html.escape(kind)}">{icon}<b>×{html.escape(qty)}</b></span>'
        )
    return "".join(html_items)


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


STYLE_PATCH = f'''
/* Recompensas: usar as imagens reais enviadas pelo utilizador */
.reward-summary{{display:none!important}}
.reward-icons{{grid-column:3 / 6;display:flex;align-items:center;justify-content:center;gap:12px;min-width:0;flex-wrap:wrap}}
.reward-chip{{display:inline-flex;align-items:center;gap:5px;white-space:nowrap}}
.reward-img{{display:inline-block;width:32px;height:32px;background-image:url("{REWARD_SPRITE}");background-repeat:no-repeat;background-size:192px 32px;flex:none}}
.reward-mystic{{background-position:0 0}}
.reward-fire{{background-position:-32px 0}}
.reward-water{{background-position:-64px 0}}
.reward-wind{{background-position:-96px 0}}
.reward-mana{{background-position:-128px 0}}
.reward-crystal{{background-position:-160px 0}}
.reward-energy{{font-size:25px;line-height:32px;display:inline-block;width:32px;text-align:center}}
.reward-chip b{{font-size:12px;color:#fff}}
.reward-unknown{{color:#aaa;font-size:12px}}
@media(max-width:1050px){{.reward-icons{{grid-column:3 / 5;gap:9px}}}}
@media(max-width:850px){{.reward-icons{{grid-column:1 / 3;grid-row:2;justify-content:flex-start;gap:9px;padding-top:2px}}.reward-chip b{{font-size:11px}}}}
@media(max-width:600px){{.reward-icons{{grid-column:1 / 3;grid-row:2;justify-content:flex-start;gap:8px}}.reward-img{{width:30px;height:30px;background-size:180px 30px}}.reward-mystic{{background-position:0 0}}.reward-fire{{background-position:-30px 0}}.reward-water{{background-position:-60px 0}}.reward-wind{{background-position:-90px 0}}.reward-mana{{background-position:-120px 0}}.reward-crystal{{background-position:-150px 0}}.reward-energy{{width:30px;font-size:22px}}.reward-chip b{{font-size:10px}}}
'''


def update_index(codes):
    text = INDEX.read_text(encoding="utf-8")
    text = re.sub(r'\n/\* Ajustes de leitura dos códigos e recompensas \*/.*?(?=\n</style>)', '', text, flags=re.S)
    text = re.sub(r'\n/\* Recompensas: apenas símbolo \+ quantidade \*/.*?(?=\n</style>)', '', text, flags=re.S)
    text = re.sub(r'\n/\* Recompensas: usar as imagens reais enviadas pelo utilizador \*/.*?(?=\n</style>)', '', text, flags=re.S)
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
