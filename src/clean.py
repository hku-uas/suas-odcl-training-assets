import os
import shutil
from pathlib import Path

from src.definitions import root_dir

dir_output = (root_dir / "output").resolve()
if not dir_output.exists():
    print(f"{dir_output} does not exist.")
    exit()

dir_datasets = list(dir_output.glob("dataset_*"))
for dir_dataset in dir_datasets:
    path_runs = dir_dataset / "runs"
    if path_runs.exists():
        print(f"Removing {path_runs}...")
        shutil.rmtree(path_runs)
    for p in dir_dataset.rglob("*.cache"):
        print(f"Removing {p}...")
        os.remove(p)
