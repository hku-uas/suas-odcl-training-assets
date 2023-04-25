import colorsys
import math
import random
from pathlib import Path

import PIL
import cv2
import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps

from src.common.enums import SuasColour, SuasShape
from src.utils.transformation import transform_coords


class CutoutLayer:
    img_shapes = []
    with Image.open(
            next(Path("../assets/foamboard_shapes").glob("*.png"), None)
    ) as all_shape_png:
        for i in range(len(list(SuasShape))):
            x = (i % 8) * 200
            y = (i // 8) * 200
            img_shapes.append(
                all_shape_png.crop((x, y, x + 200, y + 200))
            )
    font_path = next(Path("../assets/foamboard_letter_fonts").glob("*.otf"), None)
    font = ImageFont.truetype(str(font_path.resolve()), 100)

    @staticmethod
    def trace_contour_points(layer: PIL.Image):
        cv_layer = np.array(layer)

        # Split the image into its channels
        r, g, b, a = cv2.split(cv_layer)

        # Threshold the alpha channel to create a binary mask
        ret, thresh = cv2.threshold(a, 0, 255, cv2.THRESH_BINARY)

        # Find the contours of the binary mask
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        keypoints = np.vstack(contours).squeeze()

        return keypoints

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

        # Paste cardboard on canvas
        # img_shape = img_shape.resize((int(layer_size[0] * .9), int(layer_size[0] * .9)))
        points_shape = self.trace_contour_points(layer_shape)

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

        layer_shape.paste(layer_letter, (0, 0), mask=layer_letter)
        points_letter = self.trace_contour_points(layer_letter)

        # Reduce contrast of canvas
        layer_shape = ImageEnhance.Color(layer_shape).enhance(1.5)
        layer_shape = ImageEnhance.Brightness(layer_shape).enhance(3)
        layer_shape = ImageEnhance.Contrast(layer_shape).enhance(.7)
        layer_shape = layer_shape.filter(ImageFilter.GaussianBlur(radius=2))

        # Pasting the small cutout layer on the big canvas with random position and rotation
        layer_shape = layer_shape.rotate(self.rot, expand=True, resample=Image.BILINEAR)
        layer_shape = ImageOps.scale(layer_shape, .2)

        self.canvas.paste(
            layer_shape,
            box=(
                self.pos[0] - (layer_shape.size[0] // 2),
                self.pos[1] - (layer_shape.size[0] // 2)
            ),
            mask=layer_shape
        )

        self.points_shape_transformed = transform_coords(
            points_shape - (np.array(layer_size) / 2),
            self.rot,
            .2,
            self.pos
        )
        self.points_letter_transformed = transform_coords(
            points_letter - (np.array(layer_size) / 2),
            self.rot,
            .2,
            self.pos
        )

        self.bbox_shape = self.calc_bbox(self.points_shape_transformed)
        self.bbox_letter = self.calc_bbox(self.points_letter_transformed)

        self.size_shape = (
            self.bbox_shape[2] - self.bbox_shape[0],
            self.bbox_shape[3] - self.bbox_shape[1]
        )
        self.size_letter = (
            self.bbox_letter[2] - self.bbox_letter[0],
            self.bbox_letter[3] - self.bbox_letter[1]
        )

        larger_side = max(self.size_shape)
        self.bbox_padded = (
            self.pos[0] - (larger_side / 2) - 5,
            self.pos[1] - (larger_side / 2) - 5,
            self.pos[0] + (larger_side / 2) + 5,
            self.pos[1] + (larger_side / 2) + 5
        )

        # ImageDraw.Draw(self.canvas).rectangle(self.bbox_padded, outline="yellow")
        # ImageDraw.Draw(self.canvas).rectangle(self.bbox_shape, outline="blue")
        # ImageDraw.Draw(self.canvas).rectangle(self.bbox_letter, outline="red")
