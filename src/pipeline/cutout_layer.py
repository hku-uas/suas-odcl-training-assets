import colorsys
import math
import random
from pathlib import Path

import PIL
import cv2
import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps

from src.common.enums import SuasColour, SuasShape
from src.definitions import root_dir
from src.utils.transformation import transform_coords


class CutoutLayer:
    img_shapes = []
    with Image.open(
            next((root_dir / "assets" / "foamboard_shapes").glob("*.png"), None)
    ) as all_shape_png:
        for i in range(len(list(SuasShape))):
            x = (i % 8) * 200
            y = (i // 8) * 200
            img_shapes.append(
                all_shape_png.crop((x, y, x + 200, y + 200))
            )
    font_path = next((root_dir / "assets" / "foamboard_letter_fonts").glob("*.otf"), None)
    font = ImageFont.truetype(str(font_path.resolve()), 100)

    def get_corners_pos(self, bbox):
        l, t, r, b = bbox
        return [(l, t), (r, t), (r, b), (l, b)]

    def transform_image(self, img, pos, rot, scale):
        img = img.copy()
        img = img.rotate(rot, expand=True, resample=Image.BILINEAR)
        img = ImageOps.scale(img, scale)
        img_dst = Image.new(mode="RGBA", size=(512, 512))
        img_dst.paste(
            img,
            box=(
                pos[0] - (img.size[0] // 2),
                pos[1] - (img.size[0] // 2)
            ),
            mask=img
        )
        return img_dst

    @staticmethod
    def calc_bbox(coords: np.ndarray):
        return (
            coords[:, 0].min(),
            coords[:, 1].min(),
            coords[:, 0].max(),
            coords[:, 1].max()
        )

    def __init__(
            self,
            shape_colour: SuasColour,
            shape: SuasShape,
            letter_colour: SuasColour,
            letter: str
    ):
        layer_size = (512, 512)
        self.canvas = Image.new(mode="RGBA", size=layer_size)

        padding = math.ceil(self.canvas.size[0] * .1)
        self.pos = (
            random.randint(padding, self.canvas.size[0] - padding),
            random.randint(padding, self.canvas.size[0] - padding)
        )
        self.rot = random.uniform(0, 360)

        layer_shape = Image.new(mode="RGBA", size=layer_size)
        img_shape = CutoutLayer.img_shapes[shape.value]
        layer_shape.paste(
            img_shape,
            (
                int((layer_size[0] - img_shape.width) / 2),
                int((layer_size[0] - img_shape.height) / 2)
            )
        )

        # Set colour of cardboard
        # TODO fix rgb_to_hsv should input 0-1 values lollll
        shape_colour_rgba = ImageColor.getcolor(shape_colour.value, "RGB")
        shape_colour_hsv = colorsys.rgb_to_hsv(*shape_colour_rgba)
        pixel_data = layer_shape.load()
        for y in range(layer_size[0]):
            for x in range(layer_size[0]):
                a = pixel_data[x, y][3]
                if a > 0:
                    x_progress = x / layer_size[0]
                    h, s, v = shape_colour_hsv
                    pixel_colour_hsv = h, s, np.interp(x_progress, [0, 1], [v - 40, v])
                    pixel_colour_rgb = *colorsys.hsv_to_rgb(*pixel_colour_hsv), a
                    pixel_data[x, y] = tuple(int(o) for o in pixel_colour_rgb)

        layer_shape = layer_shape.rotate(self.rot, expand=True, resample=Image.BILINEAR)
        layer_shape = self.transform_image(layer_shape, self.pos, self.rot, .15)

        # Add letter to canvas
        layer_letter = Image.new(mode="RGBA", size=layer_size)
        draw = ImageDraw.Draw(layer_letter)
        _, _, w, h = draw.textbbox((0, 0), letter, font=CutoutLayer.font)
        draw.text(
            ((layer_size[0] - w) / 2, (layer_size[0] - h) / 2 - 10),
            letter,
            font=CutoutLayer.font,
            fill=letter_colour.value
        )
        layer_letter = self.transform_image(layer_letter, self.pos, self.rot, .15)

        # Reduce contrast of canvas
        layer_shape = ImageEnhance.Contrast(layer_shape).enhance(.9)
        self.canvas.paste(layer_shape, (0, 0), mask=layer_shape)
        self.canvas.paste(layer_letter, (0, 0), mask=layer_letter)
        self.canvas = ImageEnhance.Brightness(self.canvas).enhance(.9)
        self.canvas = self.canvas.filter(ImageFilter.GaussianBlur(radius=.5))

        self.bbox_shape = layer_shape.getbbox()
        self.bbox_letter = layer_letter.getbbox()

        # draw = ImageDraw.Draw(self.canvas)
        # draw.rectangle(self.bbox_shape, outline="blue")
        # draw.rectangle(self.bbox_letter, outline="red")
        # self.canvas.save("tmp.png")

        # layer_letter.save("tmp.png")
