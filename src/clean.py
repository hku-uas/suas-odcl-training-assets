import os
from pathlib import Path

if input("Are you sure [Y/n]?") != "Y":
    exit()

files = []

dataset_dir = [
    Path("../output_full"),
    Path("../output_letters"),
    Path("../output_shapes"),
]
for o in dataset_dir:
    if o.exists() and o.is_dir():
        files.extend(list(o.glob("*.png")))
        files.extend(list(o.glob("*.json")))
        files.extend(list(o.glob("*.txt")))

files = sorted(files)

for f in files:
    os.unlink(f)
