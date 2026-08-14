import html
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://summonerswarcodes.us/"
INDEX = Path("index.html")
CODE_RE = re.compile(r"\b[A-Z0-9]{8,24}\b")


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
        reward = cells[1] if len(cells) > 1 else "Recompensas"
        found.append({"code": code, "reward": reward[:180]})

    if not found:
        raise RuntimeError("Nenhum código ativo foi encontrado na fonte.")
    return found


def card(item):
    code = html.escape(item["code"])
    return f'''<article class="code" data-code="{code}"><div class="gift">🎁</div><div class="cinfo"><strong>{code}</strong><small>🔄 Atualizado automaticamente</small></div><div class="reward"><div class="ico"><span class="scroll"></span></div><b>—</b><small>Recompensa</small></div><div class="reward"><div class="ico"><span class="energy">⚡</span></div><b>—</b><small>Detalhes</small></div><div class="reward"><div class="ico"><span class="mana"></span></div><b>—</b><small>Fonte</small></div><button class="copy" onclick="copiarCodigo('{code}',this)"><span data-i18n="copy">▣ COPIAR</span></button><a class="iphone" href="https://withhive.me/313/{code}" target="_blank" rel="noopener"><span class="iphone-full"> LINK IPHONE</span><span class="iphone-short"> LINK</span></a></article>'''


def update_index(codes):
    text = INDEX.read_text(encoding="utf-8")
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
