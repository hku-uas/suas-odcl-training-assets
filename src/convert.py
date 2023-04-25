import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
from tqdm import tqdm

dataset_dir = Path("../output")
paths_img = list(dataset_dir.glob("*.png"))

output_b = Path("../output_b")
output_b.mkdir(exist_ok=True)

for path_img in tqdm(paths_img, file=sys.stdout):
    path_json = path_img.parent / (path_img.stem + ".json")
    with open(path_json, "r") as f:
        img_metadata = json.loads(f.read())

    pos = img_metadata["pos"]
    letter = img_metadata["letter"]
    size_letter = img_metadata["size_letter"]
    bbox_padded = img_metadata["bbox_padded"]

    img_full = Image.open(path_img)
    img_cropped = img_full.crop(bbox_padded)
    # img_cropped = ImageOps.grayscale(img_cropped)

    img_cropped.save(output_b / path_img.name)

    with open(output_b / f"{path_img.stem}.txt", "w", encoding="utf8") as f:
        f.write(
            f"{ord(letter) - ord('A')} "
            f".5 "
            f".5 "
            f"{size_letter[0] / img_cropped.width} "
            f"{size_letter[1] / img_cropped.height} "
        )
