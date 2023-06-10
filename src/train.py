import datetime
import os
import shutil
import sys
from pathlib import Path

from ultralytics import YOLO

from src.definitions import root_dir

if __name__ == '__main__':
    dir_output = (root_dir / "output").resolve()
    if not dir_output.exists():
        print(f"{dir_output} does not exist.")
        exit()

    dir_datasets = [
        (dir_output / "dataset_locate", 50),
        (dir_output / "dataset_identify_letters", 10),
        (dir_output / "dataset_identify_shapes", 10),
    ]

    for p, s in dir_datasets:
        if not p.exists():
            print(f"{p} does not exist.")
            exit()

    print("Deleting previously trained weights...")
    for p, s in dir_datasets:
        dir_runs_train = p / "runs"
        if not dir_runs_train.exists():
            print(f"{dir_runs_train} does not exist. Skipping...")
            continue

        print(f"Deleting {dir_runs_train}...")
        shutil.rmtree(dir_runs_train)


    def train(dir_dataset: Path, imgsz: int):
        os.chdir(str(dir_dataset))
        path_data_yaml = (dir_dataset / "data.yaml").resolve()
        model = YOLO('yolov8n.pt')
        model.train(data=str(path_data_yaml), epochs=100, imgsz=imgsz, cache="ram")


    if not "--extract" in sys.argv:
        for p, s in dir_datasets:
            print(f"Training {p}...")
            train(p, s)

    dir_weights_output = root_dir / "output" / "weights"
    for p, s in dir_datasets:
        dir_runs_detect = p / "runs" / "detect"

        subdirs = list(sorted(dir_runs_detect.glob("*")))
        if len(subdirs) == 0:
            print(f"{dir_runs_detect} does not contain any subdirectories. Skipping...")
            continue
        path_best_pt = subdirs[-1] / "weights" / "best.pt"

        if not path_best_pt.exists():
            print(f"{path_best_pt} does not exist. Skipping...")
            continue

        dir_weights_output.mkdir(exist_ok=True)
        dir_weights_output_dated = dir_weights_output / datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        dir_weights_output_dated.mkdir(exist_ok=True)

        print(f"Copying {path_best_pt} to {dir_weights_output_dated}...")
        shutil.copy(path_best_pt, dir_weights_output_dated / (p.stem + ".pt"))
