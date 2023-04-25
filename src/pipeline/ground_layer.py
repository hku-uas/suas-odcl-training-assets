import random
from pathlib import Path

from PIL import Image

from src.utils.func_static_vars import static_vars


class GroundLayer:
    aerial_bgs = []
    for bg_path in Path("../assets/bg_field").glob("*.jpg"):
        aerial_bgs.append(Image.open(bg_path))

    def __init__(self):
        # Create canvas
        self.canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 255))

        # Paste background on canvas
        bg_img = random.choice(GroundLayer.aerial_bgs).copy()
        bg_img = bg_img.rotate(random.uniform(0, 100), expand=True)
        # bg_img.thumbnail((canvas.size[0], canvas.size[1]))
        bg_img = bg_img.resize((int(self.canvas.size[0] * 2.5), int(self.canvas.size[1] * 2.5)))
        bg_offset = ((self.canvas.size[0] - bg_img.size[0]) // 2, (self.canvas.size[1] - bg_img.size[1]) // 2)
        self.canvas.paste(bg_img, bg_offset)
