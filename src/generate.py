import json
import random
import string
import sys
import uuid
from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageEnhance, ImageOps
from tqdm import tqdm

from src.enums import SuasColour, SuasShape

root_dir = Path(".").resolve()
for o in [
    root_dir / "assets",
    root_dir / "output"
]:
    if not o.exists():
        print(f"{o} does not exist. Aborting...")
        sys.exit(-1)


def generate_aerial(cutout_img: Image) -> Image:
    # Create canvas
    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 255))

    # Paste background on canvas
    bg_path = random.choice(list((root_dir / "assets" / "bg_field").glob("*.jpg")))
    bg_img = Image.open(bg_path)
    bg_img = bg_img.rotate(random.uniform(0, 100), expand=True, resample=Image.BILINEAR)
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


def get_shape_img(shape: SuasShape):
    with Image.open(
            next((root_dir / "assets" / "foamboard_shapes").glob("*.png"), None)
    ) as all_shape_png:
        shape_idx = shape.value
        x = (shape_idx % 8) * 200
        y = (shape_idx // 8) * 200
        shape_img = all_shape_png.crop((x, y, x + 200, y + 200))
    return shape_img


def main(argv):
    for i in tqdm(range(30)):
        while True:
            shape_colour = random.choice(list(SuasColour))
            letter_colour = random.choice(list(SuasColour))
            if shape_colour != letter_colour:
                break
        shape = random.choice(list(SuasShape))
        letter = random.choice(string.ascii_uppercase)

        shape_img = generate_shape(shape_colour, shape, letter_colour, letter)

        aerial_img, obj_pos_x, obj_pos_y, obj_bbox, obj_rot = generate_aerial(shape_img)
        output_stem = uuid.uuid4()
        output_path = root_dir / "output" / f"{output_stem}.png"
        aerial_img.save(output_path)
        with open(root_dir / "output" / f"{output_stem}.json", "w", encoding="utf8") as f:
            json.dump({
                "shape_colour": shape_colour.name,
                "shape": shape.name,
                "letter_colour": letter_colour.name,
                "letter": letter,
                "x": obj_pos_x,
                "y": obj_pos_y,
                "bbox": obj_bbox,
                "rot": obj_rot
            }, f, indent=4)


if __name__ == "__main__":
    main(sys.argv)
