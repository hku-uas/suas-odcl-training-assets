import json
import random
import string
import sys
import uuid
from pathlib import Path

from PIL import Image
from tqdm.contrib.concurrent import process_map

from src.common.enums import SuasColour, SuasShape
from src.pipeline.generate_cutout_layer import CutoutLayer
from src.pipeline.generate_ground_layer import GroundLayer

root_dir = Path("..").resolve()
for o in [
    root_dir / "assets",
    root_dir / "output"
]:
    if not o.exists():
        print(f"{o} does not exist. Aborting...")
        sys.exit(-1)


def generate_full(_):
    shape_colour = random.choice(list(SuasColour))
    shape = random.choice(list(SuasShape))
    letter_colour = random.choice([o for o in list(SuasColour) if o != shape_colour])
    letter = random.choice(string.ascii_uppercase)

    g = GroundLayer()
    c = CutoutLayer(shape_colour, shape, letter_colour, letter)

    o = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    o.paste(g.canvas)
    o.paste(c.canvas, mask=c.canvas)

    o.save("test.png")

    output_stem = uuid.uuid4()
    o.save(root_dir / "output" / f"{output_stem}.png")

    # Write proprietary .json
    with open(root_dir / "output" / f"{output_stem}.json", "w", encoding="utf8") as f:
        json.dump(
            {
                "shape_colour": shape_colour.name,
                "shape": shape.name,
                "letter_colour": letter_colour.name,
                "letter": letter,
                "pos": c.pos,
                "rot": c.rot,
                "bbox_shape": c.bbox_shape,
                "size_shape": c.size_shape,
                "bbox_letter": c.bbox_letter,
                "size_letter": c.size_letter,
                "bbox_padded": c.bbox_padded,
            },
            f, indent=4
        )

    # Write YOLOv8 PyTorch .txt
    with open(root_dir / "output" / f"{output_stem}.txt", "w", encoding="utf8") as f:
        f.write(
            f"0 "
            f"{c.pos[0] / o.width} "
            f"{c.pos[1] / o.height} "
            f"{c.size_shape[0] / o.width} "
            f"{c.size_shape[1] / o.height}"
        )


if __name__ == "__main__":
    if len(sys.argv) not in [1, 2]:
        print("Incorrect usage! Usage: python3 generate.py [No. of images to generate]")
        sys.exit(-1)

    no_to_generate = 30
    if len(sys.argv) == 2:
        no_to_generate = int(sys.argv[1])

    process_map(generate_full, range(0, no_to_generate), max_workers=10, file=sys.stdout, chunksize=1)

    # for i in tqdm(range(no_to_generate), file=sys.stdout):
    # generate_image(None)
