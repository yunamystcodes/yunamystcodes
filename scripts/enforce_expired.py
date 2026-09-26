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
    "AUF20NACH26SEOUL",
    "11DINGSHANGJIAN14",
    "9CHONGYASWC12",
    "XI4NHUANYINGN1",
    "LOS20GEHTS26EU",
    "REGARDEZ20LE26SWC",
    "4MINGYIDAOXIAN", "YYDSSWC26ZAN", "WASWIRDSWC2026", "INVOCATEUREU26",
    "SWCTICKET2HAMBURG", "ENTERTHESWCERA", "IGYEORA4WF2026", "SWC2026ROADTOWF",
    "OQKR1STWFNUGU", "M4ST3R37F1N4L", "S37GLORY4HOME", "JULSW2026Y1O", "SIGNUPSWC26NOW",
    "37THLGND1SWHO", "JUNSW2026W6C", "AMPRELIMSLEGACYDRP", "LEGENDSWC2026HSL",
    "YIQIZOUGUO10SWC", "GLHF2026AMERICAS", "SWC26X10LEGACYBND", "PAI2026BANGKOK",
    "APAC26LEGASEA", "HURRASWC2026", "H4MBURGISWAITING", "SWC2026JUELEBA", "912XUXIECHUANQI",
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
