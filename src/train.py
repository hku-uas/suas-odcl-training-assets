import argparse
import datetime
import os
import shutil
from pathlib import Path

from ultralytics import YOLO

from src.definitions import root_dir


def clean():
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


def export():
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Train the dataset prepared with src.generate and src.convert using Ultralytics YOLOv8 and export '
                    'them as .pt weights file under output/weights')

    parser.add_argument('--clean-only', "-c", action='store_true',
                        help='Delete previously trained weights ("runs" directories) only')
    parser.add_argument('--export-only', "-e", action='store_true',
                        help='Export the weights only after training (After .pt are generated in each dataset directory)')
    parser.add_argument("--exclude", "-t", action="append",
                        help="Exclude a dataset from cleaning, training and exporting (Specify the dataset directory name, e.g., dataset_locate)")

    args = parser.parse_args()

    dir_output = (root_dir / "output").resolve()
    if not dir_output.exists():
        print(f"{dir_output} does not exist.")
        exit()

    dir_datasets = [
        (dir_output / "dataset_locate", 64),
        (dir_output / "dataset_identify_letters", 16),
        (dir_output / "dataset_identify_shapes", 16),
    ]
    if args.exclude:
        for n in args.exclude:
            if n not in [p.stem for p, s in dir_datasets]:
                print(f"Dataset {n} does not exist.")
                exit()
            dir_datasets = [(p, s) for p, s in dir_datasets if p.stem not in args.exclude]

    if args.clean_only:
        clean()
    elif args.export_only:
        export()
    else:
        clean()

        for p, s in dir_datasets:
            if not p.exists():
                print(f"{p} does not exist.")
                exit()

        for p, s in dir_datasets:
            print(f"Training {p}...")
            train(p, s)

        export()
