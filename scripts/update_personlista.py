import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


URL = "https://data.riksdagen.se/personlista/?utformat=json&rdlstatus=tjanst"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "personlista.json"
FIELDS = ("intressent_id", "tilltalsnamn", "efternamn", "parti", "bild_url_192")


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
        {field: person.get(field, "") for field in FIELDS}
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

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"Sparade {len(snapshot)} personer i {OUTPUT}.")


if __name__ == "__main__":
    main()
