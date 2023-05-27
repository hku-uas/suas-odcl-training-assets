import random
from multiprocessing import Lock

from PIL import Image

from src.definitions import root_dir


class GroundLayer:
    aerial_bgs = []
    mutex = Lock()

    for bg_path in (root_dir / "assets" / "bg_field").glob("*.jpg"):
        aerial_bgs.append(Image.open(bg_path))

    def __init__(self):
        # Create canvas

        self.canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 255))

        # Paste background on canvas
        hmm = random.choice(GroundLayer.aerial_bgs)
        with GroundLayer.mutex:
            try:
                bg_img = hmm.copy()
            except OSError:
                print("uiyooooouiyooooouiyooooouiyooooouiyooooouiyooooouiyooooouiyooooouiyooooouiyooooouiyooooo")
                print(hmm)
                exit()

        bg_img = bg_img.rotate(random.uniform(0, 100), expand=True)
        # bg_img.thumbnail((canvas.size[0], canvas.size[1]))
        bg_img = bg_img.resize((int(self.canvas.size[0] * 2.5), int(self.canvas.size[1] * 2.5)))
        bg_offset = ((self.canvas.size[0] - bg_img.size[0]) // 2, (self.canvas.size[1] - bg_img.size[1]) // 2)
        self.canvas.paste(bg_img, bg_offset)
