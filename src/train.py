import os
from pathlib import Path

from ultralytics import YOLO

from src.definitions import root_dir

dir_output = (root_dir / "output").resolve()
if not dir_output.exists():
    print(f"{dir_output} does not exist.")
    exit()


def train(dir_dataset: Path):
    os.chdir(str(dir_dataset))
    path_data_yaml = (dir_dataset / "data.yaml").resolve()
    model = YOLO('yolov8n.pt')
    model.train(data=str(path_data_yaml), epochs=100, imgsz=100)


dir_datasets = [
    dir_output / "dataset_locate",
    dir_output / "dataset_identify_letters",
    dir_output / "dataset_identify_shapes",
]
for o in dir_datasets:
    if not o.exists():
        print(f"{o} does not exist.")
        exit()

for o in dir_datasets:
    print(f"Training {o}...")
    train(o)
