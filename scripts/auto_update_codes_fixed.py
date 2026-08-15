import html
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://summonerswarcodes.us/"
INDEX = Path("index.html")
CODE_RE = re.compile(r"\b[A-Z0-9]{8,24}\b")

# Fallbacks for codes that may appear before the external source is updated.
FALLBACK_CODES = {
    "HURRASWC2026": "Recompensas não informadas",
}


def clean(text):
    return re.sub(r"\s+", " ", html.unescape(text or "")).strip()


def fetch_codes():
    response = requests.get(
        SOURCE_URL,
        timeout=30,
        headers={"User-Agent": "YunaMystCodes/1.0 (+https://yunacodes.com/)"},
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
        if "active" not in joined.lower() and "ativo" not in joined.lower():
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

    # Never lose a known recent code if the source has not caught up yet.
    for code, reward in FALLBACK_CODES.items():
        if code not in seen:
            found.insert(0, {"code": code, "reward": reward})

    if not found:
        raise RuntimeError("Nenhum código ativo encontrado na fonte.")
    return found


def card(item):
    code = html.escape(item["code"])
    return (
        f'<article class="code" data-code="{code}">'
        f'<div class="gift">🎁</div>'
        f'<div class="cinfo"><strong>{code}</strong><small>🔄 Atualizado automaticamente</small></div>'
        f'<div class="reward-icons" aria-label="Recompensas">'
        f'<span class="reward-unknown">{html.escape(item["reward"])}</span>'
        f'</div>'
        f'<button class="copy" onclick="copiarCodigo(\'{code}\',this)"><span data-i18n="copy">▣ COPIAR</span></button>'
        f'<a class="iphone" href="https://withhive.me/313/{code}" target="_blank" rel="noopener">'
        f'<span class="iphone-full"> LINK IPHONE</span><span class="iphone-short"> LINK</span></a>'
        f'</article>'
    )


def update_index(codes):
    text = INDEX.read_text(encoding="utf-8")
    marker = '<div class="codes" id="activeCodesList">'
    start = text.find(marker)
    if start == -1:
        raise RuntimeError("Bloco da lista de códigos ativos não encontrado.")

    content_start = start + len(marker)

    # Find the closing div that is immediately followed by the existing
    # "more/expired" section, tolerating whitespace/newlines and attributes.
    match = re.search(r'</div>\s*<div\s+class="more"', text[content_start:], re.I)
    if not match:
        match = re.search(r'</div>\s*<div[^>]*class="[^"]*more[^"]*"', text[content_start:], re.I)
    if not match:
        raise RuntimeError("Fim da lista de códigos ativos não encontrado.")

    end = content_start + match.start() + len('</div>')
    cards = "\n".join(card(item) for item in codes)
    new_text = text[:content_start] + "\n" + cards + "\n" + text[end:]
    INDEX.write_text(new_text, encoding="utf-8")


if __name__ == "__main__":
    codes = fetch_codes()
    update_index(codes)
    print("Códigos ativos atualizados:", ", ".join(x["code"] for x in codes))
