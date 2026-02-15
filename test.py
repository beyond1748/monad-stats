from pathlib import Path
import os

out_dir = Path("data/")
out_dir.mkdir(parents=True, exist_ok=True)

(out_dir / "test.txt").write_text("test action:tm:\n" + os.environ["data"])
print("mmokay")
