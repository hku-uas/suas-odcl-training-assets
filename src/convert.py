import json
import string
import sys
from pathlib import Path

from PIL import Image
from tqdm.contrib.concurrent import process_map

from src.common.enums import SuasShape

output_full = Path("../output")
paths_img = list(output_full.glob("*.png"))

output_shapes = Path("../output_shapes")
output_shapes.mkdir(exist_ok=True)

output_letters = Path("../output_letters")
output_letters.mkdir(exist_ok=True)


def convert(path_img):
    path_json = path_img.parent / (path_img.stem + ".json")
    with open(path_json, "r") as f:
        img_metadata = json.loads(f.read())

    img_full = Image.open(path_img)
    img_cropped = img_full.crop(img_metadata["bbox_padded"])
    # img_cropped = ImageOps.grayscale(img_cropped)

    img_cropped.save(output_shapes / path_img.name)
    img_cropped.save(output_letters / path_img.name)

    shape_w, shape_h = img_metadata["size_shape"]
    letter_w, letter_h = img_metadata["size_letter"]

    shape_w *= 1.02
    shape_h *= 1.02
    letter_w *= 1.02
    letter_h *= 1.02

    with open(output_shapes / f"{path_img.stem}.txt", "w", encoding="utf8") as f:
        f.write(
            f'{int(SuasShape[img_metadata["shape"]])} '
            f'.5 '
            f'.5 '
            f'{shape_w / img_cropped.width} '
            f'{shape_h / img_cropped.height} '
        )

    with open(output_letters / f"{path_img.stem}.txt", "w", encoding="utf8") as f:
        f.write(
            f'{ord(img_metadata["letter"]) - ord("A")} '
            f'.5 '
            f'.5 '
            f'{letter_w / img_cropped.width} '
            f'{letter_h / img_cropped.height} '
        )


if __name__ == '__main__':
    with open(output_shapes / "_.labels", "w") as f:
        f.write("\n".join(list([o.name for o in SuasShape])))
    with open(output_letters / "_.labels", "w") as f:
        f.write("\n".join(list(string.ascii_uppercase)))

    process_map(convert, paths_img, max_workers=10, file=sys.stdout)
    # convert(paths_img[0])
