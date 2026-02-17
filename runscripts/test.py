from pathlib import Path
import os
from datetime import datetime

out_dir = Path("data/")
out_dir.mkdir(parents=True, exist_ok=True)

(out_dir / "test.txt").write_text("test action:tm:\n" + os.environ["data"] + f"\n{datetime.now().isoformat() + 'Z'}")
print("mmokay")
