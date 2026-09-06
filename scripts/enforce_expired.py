import json
from pathlib import Path
from bs4 import BeautifulSoup

INDEX = Path("index.html")
HISTORY = Path("data/code_history.json")

# Confirmed expired codes. These are never allowed back into the active list.
KNOWN_EXPIRED = {
    "2SOREIKENIPPON6",
    "2SWCTORONTOTHE6IX",
    "APAC1K0UB4NGK0K",
    "AUGSW2026V7N",
    "LAST4PUNCHIN",
    "SWCJOAAAKR26",
    "SWGAJA2BKK",
}


def main():
    history = {}
    if HISTORY.exists():
        try:
            history = json.loads(HISTORY.read_text(encoding="utf-8"))
        except Exception:
            history = {}

    # Preserve every code that has already been confirmed expired. The updater
    # can temporarily mark an old code active when a source still lists it;
    # expired_at is the persistent signal that prevents it from returning.
    expired_codes = set(KNOWN_EXPIRED)
    for code, record in history.items():
        if record.get("status") == "expired" or record.get("expired_at"):
            expired_codes.add(code.upper())

    for code in expired_codes:
        record = history.get(code, {"code": code, "reward": "Recompensa não informada", "sources": []})
        record["code"] = code
        record["status"] = "expired"
        history[code] = record

    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(
        json.dumps(history, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    soup = BeautifulSoup(INDEX.read_text(encoding="utf-8"), "html.parser")
    active = soup.find(id="activeCodesList")
    removed = []
    if active is not None:
        for card in list(active.select("[data-code]")):
            code = card.get("data-code", "").upper()
            if code in expired_codes:
                removed.append(code)
                card.decompose()

    # Remove duplicate copies from the expired panel; the main updater will
    # rebuild the panel from history on its next run.
    expired_panel = soup.find(class_="expired-panel")
    if expired_panel is not None:
        for card in list(expired_panel.select("[data-code]")):
            if card.get("data-code", "").upper() in expired_codes:
                card.decompose()

    INDEX.write_text(str(soup), encoding="utf-8")
    print("Códigos expirados removidos:", ", ".join(sorted(set(removed))))


if __name__ == "__main__":
    main()
