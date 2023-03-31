import json
import random
import string
import sys
import time
import uuid
from math import ceil
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageEnhance, ImageOps
from tqdm import tqdm

from enums import SuasColour, SuasShape

root_dir = Path(".").resolve()
for o in [
    root_dir / "assets",
    root_dir / "output"
]:
    if not o.exists():
        print(f"{o} does not exist. Aborting...")
        sys.exit(-1)


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


@static_vars(aerial_bgs=None)
def generate_aerial(cutout_img: Image) -> Image:
    # Load all aerial backgrounds and cache them
    if generate_aerial.aerial_bgs is None:
        generate_aerial.aerial_bgs = []
        for bg_path in (root_dir / "assets" / "bg_field").glob("*.jpg"):
            generate_aerial.aerial_bgs.append(
                Image.open(bg_path)
            )

    # Create canvas
    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 255))

    # Paste background on canvas
    bg_img = random.choice(generate_aerial.aerial_bgs).copy()
    bg_img = bg_img.rotate(random.uniform(0, 100), expand=True)
    # bg_img.thumbnail((canvas.size[0], canvas.size[1]))
    bg_img = bg_img.resize((int(canvas.size[0] * 2.5), int(canvas.size[1] * 2.5)))
    bg_offset = ((canvas.size[0] - bg_img.size[0]) // 2, (canvas.size[1] - bg_img.size[1]) // 2)
    canvas.paste(bg_img, bg_offset)

    # Paste cutout on canvas
    cutout = cutout_img.copy()

    obj_rot = random.uniform(0, 360)
    cutout = cutout.rotate(obj_rot, expand=True, resample=Image.BILINEAR)

    cutout = ImageOps.contain(cutout, (int(canvas.size[0] * .05), int(canvas.size[0] * .05)))

    enhancer = ImageEnhance.Brightness(cutout)
    cutout = enhancer.enhance(0.8)

    padding = ceil(canvas.size[0] * .1)
    obj_pos_x = random.randint(padding, canvas.size[0] - padding)
    obj_pos_y = random.randint(padding, canvas.size[0] - padding)
    obj_bbox = (
        obj_pos_x - (cutout.size[0] // 2),
        obj_pos_y - (cutout.size[0] // 2),
        obj_pos_x + (cutout.size[0] // 2),
        obj_pos_y + (cutout.size[0] // 2),
    )
    canvas.paste(cutout, box=(obj_bbox[0], obj_bbox[1]), mask=cutout)

    # Uncomment if want red frame
    # ImageDraw.Draw(canvas).rectangle(obj_bbox, outline="red")

    # Returning the canvas
    return canvas, obj_pos_x, obj_pos_y, obj_bbox, obj_rot


def generate_shape(
        shape_colour: SuasColour,
        shape: SuasShape,
        letter_colour: SuasColour,
        letter: str
) -> Image:
    canvas = Image.new(mode="RGBA", size=(200, 200))

    shape_img: Image = get_shape_img(shape).copy()
    pixel_data = shape_img.load()
    width, height = canvas.size
    for y in range(height):
        for x in range(width):
            if pixel_data[x, y][3] != 0:
                pixel_data[x, y] = ImageColor.getcolor(shape_colour.value, "RGBA")
    canvas.paste(shape_img, (0, 0))

    draw = ImageDraw.Draw(canvas)
    font_path = (root_dir / "assets" / "foamboard_letter_fonts").glob("*.otf").__next__()
    font = ImageFont.truetype(str(font_path.resolve()), 100)
    _, _, w, h = draw.textbbox((0, 0), letter, font=font)
    draw.text(((200 - w) / 2, (200 - h) / 2 - 10), letter, font=font, fill=letter_colour.value)

    return canvas


@static_vars(all_shape_imgs=None)
def get_shape_img(shape: SuasShape):
    if get_shape_img.all_shape_imgs is None:
        get_shape_img.all_shape_imgs = []
        with Image.open(
                next((root_dir / "assets" / "foamboard_shapes").glob("*.png"), None)
        ) as all_shape_png:
            for i in range(len(list(SuasShape))):
                x = (i % 8) * 200
                y = (i // 8) * 200
                get_shape_img.all_shape_imgs.append(
                    all_shape_png.crop((x, y, x + 200, y + 200))
                )
    return get_shape_img.all_shape_imgs[shape.value]


@static_vars(last=time.perf_counter())
def stopwatch(section_name: Optional[str] = None):
    now = time.perf_counter()
    elapsed = now - stopwatch.last
    if section_name is not None:
        tqdm.write(f"[Stopwatch][{section_name}]: {elapsed:.4f}s")
    stopwatch.last = time.perf_counter()


def main(argv):
    no_to_generate = 30
    if len(argv) == 2:
        no_to_generate = int(argv[1])
    for i in tqdm(range(no_to_generate), file=sys.stdout):
        while True:
            shape_colour = random.choice(list(SuasColour))
            letter_colour = random.choice(list(SuasColour))
            if shape_colour != letter_colour:
                break
        shape = random.choice(list(SuasShape))
        letter = random.choice(string.ascii_uppercase)

        # stopwatch()

        shape_img = generate_shape(shape_colour, shape, letter_colour, letter)
        # stopwatch("generate_shape")

        aerial_img, obj_pos_x, obj_pos_y, obj_bbox, obj_rot = generate_aerial(shape_img)
        obj_width = obj_bbox[2] - obj_bbox[0]
        obj_height = obj_bbox[3] - obj_bbox[1]
        # stopwatch("generate_aerial")

        json_content = {
            "shape_colour": shape_colour.name,
            "shape": shape.name,
            "letter_colour": letter_colour.name,
            "letter": letter,
            "x": obj_pos_x,
            "y": obj_pos_y,
            "bbox": obj_bbox,
            "rot": obj_rot
        }

        output_stem = uuid.uuid4()
        aerial_img.save(root_dir / "output" / f"{output_stem}.png")
        with open(root_dir / "output" / f"{output_stem}.json", "w", encoding="utf8") as f:
            json.dump(json_content, f, indent=4)

        width, height = aerial_img.size[0], aerial_img.size[1]

        with open(root_dir / "output" / f"{output_stem}.txt", "w", encoding="utf8") as f:
            f.write(f"0 {obj_pos_x / width} {obj_pos_y / height} {obj_width / width} {obj_height / height}")


if __name__ == "__main__":
    if len(sys.argv) not in [1, 2]:
        print("Incorrect usage! Usage: python3 generate.py [No. of images to generate]")
        sys.exit(-1)
    main(sys.argv)
