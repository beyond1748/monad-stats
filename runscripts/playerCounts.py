import csv
from datetime import datetime
from pathlib import Path
import os
import requests

UNIVERSES = {
    'deepwoken': '1359573625',
    'cursedgear': '3726919761',
    'deeptesting': '1966100065',
    'roguelineage': '1087859240'
}

OUT_DIR = Path("data/playercounts")

def save_player_count(filename, visits, player_count):
    now = datetime.now()
    csv_file = OUT_DIR / f"{filename}"
    
    file_exists = csv_file.exists()
    
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        
        if not file_exists:
            writer.writerow(['timestamp', 'visits', 'player_count'])
        
        timestamp = now.isoformat() + 'Z'
        writer.writerow([timestamp, visits, player_count])


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

    resp = session.get(f"https://games.roblox.com/v1/games?universeIds={','.join(UNIVERSES.values())}", timeout=30)
    resp.raise_for_status()
    places_payload = resp.json()

    data = places_payload.get("data", [])
    if not isinstance(data, list) or not data:
        print("No data returned. Exiting.")
        return

    names = list(UNIVERSES.keys())
    for i, item in enumerate(data):
        # print(item)
        save_player_count(f"{names[i]}.csv", item["visits"], item["playing"])



if __name__ == "__main__":
    main()
