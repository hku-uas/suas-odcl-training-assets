import json
import string
import sys
from pathlib import Path

import yaml
from PIL import Image
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

from src.common.enums import SuasShape
from src.definitions import root_dir


class Convert:
    def __init__(self):
        self.dir_output = root_dir / "output"

        self.dir_ds_locate = self.dir_output / "dataset_locate"
        self.dir_ds_identify_shape = self.dir_output / "dataset_identify_shapes"
        self.dir_ds_identify_letter = self.dir_output / "dataset_identify_letters"

        self.paths_img = list((self.dir_output / "raw").glob("*.png"))

        files_to_be_cleaned = []
        for o in [self.dir_ds_locate, self.dir_ds_identify_shape, self.dir_ds_identify_letter]:
            for p in o.rglob("*"):
                if p.is_dir():
                    continue
                if p.suffix not in [".jpg", ".png", ".txt", ".yaml"]:
                    print(f"Abnormal file in directories: {p}")
                    exit()
                files_to_be_cleaned.append(p)

        print("Cleaning directories...")
        for p in tqdm(files_to_be_cleaned, file=sys.stdout):
            p.unlink()

        print("Creating directories...")

        for i, dir_ds in enumerate([
            self.dir_ds_locate,
            self.dir_ds_identify_shape,
            self.dir_ds_identify_letter
        ]):
            dir_ds.mkdir(exist_ok=True)
            for a in ["train", "valid", "test"]:
                (dir_ds / a).mkdir(exist_ok=True)
                for b in ["images", "labels"]:
                    (dir_ds / a / b).mkdir(exist_ok=True)
            classes = [
                ["cutout"],
                list([o.name for o in SuasShape]),
                list(string.ascii_uppercase)
            ][i]
            with open(dir_ds / "data.yaml", "w") as f:
                yaml.dump({
                    "train": "../train/images",
                    "val": "../valid/images",
                    "test": "../test/images",
                    "nc": len(classes),
                    "names": classes
                }, f)

    def run(self):
        print("Generating dataset...")
        process_map(self.convert, self.paths_img, max_workers=None, file=sys.stdout)
        # convert(paths_img[0])

    def convert(self, path_img: Path):
        loc = self.paths_img.index(path_img) / len(self.paths_img)
        set_name = "test" if loc > .9 else ("valid" if loc > .7 else "train")

        path_json = path_img.parent / (path_img.stem + ".json")
        with open(path_json, "r") as f:
            d = json.loads(f.read())

        img_full = Image.open(path_img)
        img_cropped = img_full.crop(d["bbox_padded"])
        # img_cropped = ImageOps.grayscale(img_cropped)

        img_full.save(self.dir_ds_locate / set_name / "images" / path_img.name)
        img_cropped.save(self.dir_ds_identify_shape / set_name / "images" / path_img.name)
        img_cropped.save(self.dir_ds_identify_letter / set_name / "images" / path_img.name)

        shape_w, shape_h = d["size_shape"]
        letter_w, letter_h = d["size_letter"]

        with open(self.dir_ds_locate / set_name / "labels" / f"{path_img.stem}.txt", "w") as f:
            f.write(
                f'{int(SuasShape[d["shape"]])} '
                f'{d["pos"][0] / img_full.width} '
                f'{d["pos"][1] / img_full.height} '
                f'{shape_w / img_full.width} '
                f'{shape_h / img_full.height} '
            )

        with open(self.dir_ds_identify_shape / set_name / "labels" / f"{path_img.stem}.txt", "w") as f:
            f.write(
                f'{int(SuasShape[d["shape"]])} '
                f'.5 '
                f'.5 '
                f'{shape_w / img_cropped.width} '
                f'{shape_h / img_cropped.height} '
            )

        with open(self.dir_ds_identify_letter / set_name / "labels" / f"{path_img.stem}.txt", "w") as f:
            f.write(
                f'{ord(d["letter"]) - ord("A")} '
                f'.5 '
                f'.5 '
                f'{letter_w / img_cropped.width} '
                f'{letter_h / img_cropped.height} '
            )


if __name__ == '__main__':
    Convert().run()
