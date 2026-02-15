from pathlib import Path
import json
import time
import hashlib
import os
from datetime import datetime, timezone

import requests


OUT_DIR = Path("data/cursedgear")
UNIVERSE_ID = 3726919761




def stable_json_bytes(obj) -> bytes:
    # stable ordered json, yea
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def latest_json_file(folder: Path) -> Path | None:
    files = sorted(folder.glob("*.json"))
    return files[-1] if files else None


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Roblox/WinInet",
            "Cookie": f".ROBLOSECURITY={os.environ["cookie"]}",
            "Accept": "application/json",
        }
    )

    # get all places id
    resp = session.get("https://develop.roblox.com/v1/universes/3726919761/places?sortOrder=Asc&limit=100", timeout=30)
    resp.raise_for_status()
    places_payload = resp.json()

    places = places_payload.get("data", [])
    if not isinstance(places, list) or not places:
        print("No places returned. Exiting.")
        return

    place_ids = [p.get("id") for p in places if isinstance(p, dict) and "id" in p]
    place_ids = [pid for pid in place_ids if pid is not None]

    if not place_ids:
        print("No place IDs found. Exiting.")
        return

    print(f"Found {len(place_ids)} place IDs.")

    # get place infos
    all_details = {}

    for i, place_id in enumerate(place_ids, start=1):
        url = f"https://economy.roblox.com/v2/assets/{place_id}/details"

        # Small delay to reduce rate-limit risk
        time.sleep(0.2)

        try:
            r = session.get(url, timeout=30)
            r.raise_for_status()
            details = r.json()
            all_details[str(place_id)] = details
            print(f"[{i}/{len(place_ids)}] OK {place_id}")
        except Exception as e:
            print(f"[{i}/{len(place_ids)}] FAILED {place_id}: {e}")

    # compare
    new_bytes = stable_json_bytes(all_details)
    new_hash = sha256_bytes(new_bytes)

    latest = latest_json_file(OUT_DIR)

    if latest and latest.exists():
        try:
            old_obj = json.loads(latest.read_text(encoding="utf-8"))
            old_bytes = stable_json_bytes(old_obj)
            old_hash = sha256_bytes(old_bytes)

            if old_hash == new_hash:
                print(f"No changes vs latest file: {latest.name}")
                print("Stopping without writing.")
                return
        except Exception as e:
            print(f"Could not read/parse latest file {latest.name}: {e}")
            print("Will write a new file anyway.")

    # save new file
    ts = (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
    out_path = OUT_DIR / f"{ts}.json"

    out_path.write_text(
        json.dumps(all_details, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
