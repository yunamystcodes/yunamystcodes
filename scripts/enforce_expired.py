import json
from pathlib import Path
from bs4 import BeautifulSoup

INDEX = Path("index.html")
HISTORY = Path("data/code_history.json")

# Codes confirmed expired and never allowed back into the active list.
KNOWN_EXPIRED = {
    "2SOREIKENIPPON6",
}


def main():
    # Mark known expired codes in the persistent history.
    history = {}
    if HISTORY.exists():
        try:
            history = json.loads(HISTORY.read_text(encoding="utf-8"))
        except Exception:
            history = {}

    for code in KNOWN_EXPIRED:
        record = history.get(code, {"code": code, "reward": "Recompensa não informada", "sources": []})
        record["code"] = code
        record["status"] = "expired"
        history[code] = record

    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # Remove known expired codes from the active list in the generated page.
    soup = BeautifulSoup(INDEX.read_text(encoding="utf-8"), "html.parser")
    active = soup.find(id="activeCodesList")
    if active is not None:
        for card in active.select("[data-code]"):
            if card.get("data-code", "").upper() in KNOWN_EXPIRED:
                card.decompose()

    # Also remove them from the expired panel if the updater inserted a duplicate.
    expired_panel = soup.find(class_="expired-panel")
    if expired_panel is not None:
        for card in expired_panel.select("[data-code]"):
            if card.get("data-code", "").upper() in KNOWN_EXPIRED:
                card.decompose()

    INDEX.write_text(str(soup), encoding="utf-8")
    print("Códigos expirados removidos da área ativa:", ", ".join(sorted(KNOWN_EXPIRED)))


if __name__ == "__main__":
    main()
