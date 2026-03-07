import csv
from datetime import datetime
from pathlib import Path
import os
import requests

def main():
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Roblox/WinInet",
            "Cookie": f".ROBLOSECURITY={os.environ["cookie"]}",
            "Accept": "application/json",
        }
    )

    resp = session.get(f"https://apis.roblox.com/platform-chat-api/v1/metadata", timeout=30)
    print(resp.text)



if __name__ == "__main__":
    main()
