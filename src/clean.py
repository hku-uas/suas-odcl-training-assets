import os
from pathlib import Path

from src.definitions import root_dir

if input("Are you sure [Y/n]?") != "Y":
    exit()

files = []

dataset_dir = [
    (root_dir / "output"),
    (root_dir / "output_full"),
    (root_dir / "output_letters"),
    (root_dir / "output_shapes"),
]
for o in dataset_dir:
    if o.exists() and o.is_dir():
        files.extend(list(o.glob("*.png")))
        files.extend(list(o.glob("*.json")))
        files.extend(list(o.glob("*.txt")))

files = sorted(files)

for f in files:
    os.unlink(f)
