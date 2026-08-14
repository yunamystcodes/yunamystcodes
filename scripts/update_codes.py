import html
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://summonerswarcodes.us/"
INDEX = Path("index.html")
CODE_RE = re.compile(r"\b[A-Z0-9]{8,24}\b")

# Códigos de eventos recentes que podem não aparecer na tabela principal da fonte.
# Mantemos a recompensa como "não confirmada" quando não existe uma fonte fiável
# publicada para não inventar recompensas.
EXTRA_CODES = {
    "SWCTICKET2HAMBURG": "Recompensa SWC — não confirmada",
    "INVOCATEUREU26": "Recompensa SWC — não confirmada",
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

    # Recompensas confirmadas recentemente para os códigos que aparecem no site.
    reward_overrides = {
        "AUGSW2026V7N": "100 Energia + 1 Pergaminho de Fogo",
        "SWXFRIEREN2026": "100 Energia + 300.000 Mana + 3 Pergaminhos Místicos",
    }
    for item in found:
        if item["code"] in reward_overrides:
            item["reward"] = reward_overrides[item["code"]]

    # Acrescenta os códigos SWC recentes caso a fonte principal ainda não os tenha na tabela.
    for code, reward in EXTRA_CODES.items():
        if code not in seen:
            found.insert(0, {"code": code, "reward": reward})
            seen.add(code)

    if not found:
        raise RuntimeError("Nenhum código ativo foi encontrado na fonte.")
    return found


def card(item):
    code = html.escape(item["code"])
    reward = html.escape(item["reward"] or "Recompensa não informada")
    return f'''<article class="code" data-code="{code}"><div class="gift">🎁</div><div class="cinfo"><strong>{code}</strong><small>🔄 Atualizado automaticamente</small></div><div class="reward-summary"><small>RECOMPENSA</small><b>{reward}</b></div><button class="copy" onclick="copiarCodigo('{code}',this)"><span data-i18n="copy">▣ COPIAR</span></button><a class="iphone" href="https://withhive.me/313/{code}" target="_blank" rel="noopener"><span class="iphone-full"> LINK IPHONE</span><span class="iphone-short"> LINK</span></a></article>'''


def update_index(codes):
    text = INDEX.read_text(encoding="utf-8")

    # Ajustes visuais permanentes, preservados nas futuras atualizações automáticas.
    style_patch = '''\n/* Ajustes de leitura dos códigos e recompensas */\n.reward-summary{grid-column:3 / 6;text-align:center;min-width:0;padding:0 4px}.reward-summary small{display:block;color:#d7cbdc;font-size:9px;letter-spacing:.4px;margin-bottom:3px}.reward-summary b{display:block;color:#fff;font-size:12px;line-height:1.25;white-space:normal}.cinfo strong{font-size:16px}.cinfo small{font-size:11px}\n@media(max-width:600px){.cinfo strong{font-size:14px}.cinfo small{font-size:10px}.reward-summary{grid-column:1 / 3;grid-row:2;text-align:center;padding:0 2px}.reward-summary b{font-size:11px;line-height:1.2}.reward-summary small{font-size:8px}.code .copy{grid-row:3}.code .iphone{grid-row:3}}\n@media(max-width:380px){.cinfo strong{font-size:13px}.reward-summary b{font-size:10px}.code .copy,.code .iphone{font-size:11px}}\n'''
    if '/* Ajustes de leitura dos códigos e recompensas */' not in text:
        text = text.replace('</style>', style_patch + '</style>', 1)

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

# Mantém a geração do index sincronizada com o repositório.
