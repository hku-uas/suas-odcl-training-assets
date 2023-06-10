import os
from pathlib import Path

from ultralytics import YOLO

from src.definitions import root_dir

if __name__ == '__main__':
    dir_output = (root_dir / "output").resolve()
    if not dir_output.exists():
        print(f"{dir_output} does not exist.")
        exit()


    def train(dir_dataset: Path, imgsz: int):
        os.chdir(str(dir_dataset))
        path_data_yaml = (dir_dataset / "data.yaml").resolve()
        model = YOLO('yolov8n.pt')
        model.train(data=str(path_data_yaml), epochs=100, imgsz=imgsz, cache="ram")


    dir_datasets = [
        (dir_output / "dataset_locate", 50),
        (dir_output / "dataset_identify_letters", 10),
        (dir_output / "dataset_identify_shapes", 10),
    ]
    for p, s in dir_datasets:
        if not p.exists():
            print(f"{p} does not exist.")
            exit()

    for p, s in dir_datasets:
        print(f"Training {p}...")
        train(p, s)
