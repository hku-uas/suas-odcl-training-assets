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
    model.train(data=str(path_data_yaml), epochs=100, imgsz=640)


for o in dir_output.glob("dataset_locate"):
    train(o)
