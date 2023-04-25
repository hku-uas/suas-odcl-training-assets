import os
from pathlib import Path

files = []

dataset_dir = [Path("../output"), Path("../output_b")]
for o in dataset_dir:
    if o.exists() and o.is_dir():
        files.extend(list(o.glob("*.png")))
        files.extend(list(o.glob("*.json")))

files = sorted(files)

for f in files:
    os.unlink(f)
