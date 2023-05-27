import json
import string
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageOps
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

from src.common.enums import SuasShape
from src.definitions import root_dir
from src.utils.transformation import transform_coords


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
                if p.suffix not in [".jpg", ".png", ".txt", ".yaml", ".pt", ".cache", ".csv"]:
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
                ["cutout", "emergent"],
                list([o.name for o in SuasShape]),
                list(string.ascii_uppercase)
            ][i]
            with open(dir_ds / "data.yaml", "w") as f:
                yaml.dump({
                    "train": "./train/images",
                    "val": "./valid/images",
                    "test": "./test/images",
                    "nc": len(classes),
                    "names": classes
                }, f)

    def run(self):
        print("Generating dataset...")
        process_map(self.convert, self.paths_img, max_workers=None, file=sys.stdout, chunksize=1)
        # self.convert(self.paths_img[0])

    def bbox_pos(self, bbox):
        l, t, r, b = bbox
        return (l + r) / 2, (t + b) / 2

    def bbox_size(self, bbox):
        l, t, r, b = bbox
        w, h = r - l, b - t
        return w, h

    def find_max_length(self, bbox):
        w, h = self.bbox_size(bbox)
        return max(w, h)

    # Find bbox center pos, make new bbox which centers it and pads it to be a square
    def expand_bbox(self, bbox, length):
        x, y = self.bbox_pos(bbox)
        return x - length / 2, y - length / 2, x + length / 2, y + length / 2

    def convert(self, path_img: Path):
        loc = self.paths_img.index(path_img) / len(self.paths_img)
        set_name = "test" if loc > .9 else ("valid" if loc > .7 else "train")

        path_json = path_img.parent / (path_img.stem + ".json")
        with open(path_json, "r") as f:
            d = json.loads(f.read())

        img_full = Image.open(path_img)
        img_full.save(self.dir_ds_locate / set_name / "images" / path_img.name)

        bbox_shape = d["bbox_shape"]
        pos_shape = self.bbox_pos(bbox_shape)
        bbox_letter = d["bbox_letter"]
        cropped_bbox_length = max(self.bbox_size(bbox_shape)) + 10

        img_shape_cropped = img_full.crop(self.expand_bbox(bbox_shape, cropped_bbox_length))
        img_shape_cropped = ImageOps.grayscale(img_shape_cropped)
        img_shape_cropped.save(self.dir_ds_identify_shape / set_name / "images" / path_img.name)

        img_letter_cropped = img_full.crop(self.expand_bbox(bbox_letter, cropped_bbox_length))
        img_letter_cropped = ImageOps.grayscale(img_letter_cropped)
        img_letter_cropped.save(self.dir_ds_identify_letter / set_name / "images" / path_img.name)

        shape_w, shape_h = self.bbox_size(bbox_shape)
        letter_w, letter_h = self.bbox_size(bbox_letter)

        with open(self.dir_ds_locate / set_name / "labels" / f"{path_img.stem}.txt", "w") as f:
            f.write(
                f'0 '
                f'{pos_shape[0] / img_full.width} '
                f'{pos_shape[1] / img_full.height} '
                f'{shape_w / img_full.width} '
                f'{shape_h / img_full.height} '
            )

        with open(self.dir_ds_identify_shape / set_name / "labels" / f"{path_img.stem}.txt", "w") as f:
            f.write(
                f'{int(SuasShape[d["shape"]])} '
                f'.5 '
                f'.5 '
                f'{shape_w / img_shape_cropped.width} '
                f'{shape_h / img_shape_cropped.height} '
            )

        with open(self.dir_ds_identify_letter / set_name / "labels" / f"{path_img.stem}.txt", "w") as f:
            f.write(
                f'{ord(d["letter"]) - ord("A")} '
                f'.5 '
                f'.5 '
                f'{letter_w / img_letter_cropped.width} '
                f'{letter_h / img_letter_cropped.height} '
            )


if __name__ == '__main__':
    Convert().run()
