import json
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path


URL = "https://data.riksdagen.se/personlista/?utformat=json&rdlstatus=tjanst"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "personlista.json"
FIELDS = ("intressent_id", "tilltalsnamn", "efternamn", "parti", "bild_url_192")
PARTY_CODES = {"S", "M", "SD", "C", "V", "KD", "MP", "L"}
COMMITTEE_CODES = {
    "AU", "CU", "FiU", "FöU", "JuU", "KU", "KrU", "MJU",
    "NU", "SkU", "SoU", "SfU", "TU", "UbU", "UU",
}


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def current_committees(person, today):
    assignments = person.get("personuppdrag", {})
    if not isinstance(assignments, dict):
        return []

    committees = set()
    for assignment in as_list(assignments.get("uppdrag")):
        if not isinstance(assignment, dict):
            continue

        code = assignment.get("organ_kod")
        if code not in COMMITTEE_CODES:
            continue

        starts = assignment.get("from", "")
        ends = assignment.get("tom", "")
        start_date = date.fromisoformat(starts[:10]) if starts else date.min
        end_date = date.fromisoformat(ends[:10]) if ends else date.max
        if start_date <= today <= end_date:
            committees.add(code)

    return sorted(committees)


def main():
    request = urllib.request.Request(URL, headers={"User-Agent": "riksdagsmemory-data-refresh"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.load(response)
            break
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            if attempt == 2:
                raise
            print(f"API-hämtning misslyckades ({attempt + 1}/3): {error}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))

    people = payload.get("personlista", {}).get("person")
    if not isinstance(people, list):
        raise ValueError("Riksdagens API returnerade inte en personlista.")

    snapshot = [
        {
            **{field: person.get(field, "") for field in FIELDS},
            "utskott": current_committees(person, date.today()),
        }
        for person in people
        if (
            isinstance(person, dict)
            and person.get("intressent_id")
            and person.get("parti")
            and person.get("bild_url_192")
        )
    ]
    if len(snapshot) < 12:
        raise ValueError(f"API-svaret innehöll oväntat få personer med bild: {len(snapshot)}.")
    small_parties = [
        code for code in PARTY_CODES
        if sum(person["parti"] == code for person in snapshot) < 12
    ]
    if small_parties:
        raise ValueError(f"För få spelbara personer i partier: {', '.join(sorted(small_parties))}.")
    small_committees = [
        code for code in COMMITTEE_CODES
        if sum(code in person["utskott"] for person in snapshot) < 12
    ]
    if small_committees:
        raise ValueError(f"För få spelbara personer i utskott: {', '.join(sorted(small_committees))}.")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"Sparade {len(snapshot)} personer i {OUTPUT}.")


if __name__ == "__main__":
    main()
