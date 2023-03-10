# ODCL Training Asset

Artificially generated images for training ODCL (Object Detection, Classification, Localization) in SUAS Competition.

![](https://raw.githubusercontent.com/hku-uas/suas-odcl-training-assets/master/output/39b4be6e-61b3-4fcd-800e-b6757c38eaa4.png)

---

From the 2023 SUAS Competition rule book,

> UAS should be able to search for objects. Teams must detect, classify, and localize two types of objects: standard and
> emergent. Each object is located in the Air Drop Boundary and marks the target for an air drop. A standard object will
> be a colored alphanumeric (uppercase letter or number) on a colored shape. The standard object will be printed onto
> 8.5” x 11” paper, cut out, and secured to the ground (e.g. with cardboard backing and tape). The emergent object is a
> manikin dressed in clothes. There will be at most one emergent object.

**TLDR:** Two types of objects are spread across the airfield, 'standard object' (~30+ cardboard cutouts), and 'emergent
object' (1 manikin). The drone should locate all of them and return their coordinates.

Cardboard cutout is a piece of cardboard cut into generic shapes (e.g. circle, triangle, square), and coloured with
simple colours (e.g. red, green, black) (For a full list of shapes and colours, refer to the lists below). They all have
a big capital letter on them. For cardboard cutouts, the drone should also be able to recognise the shape, colour and
letter on it.

This repository contains scripts and the generated images for training the OCDL (Object Detection, Classification,
Localization) of the above objects.

## Generating Images

By default, there are some example images inside `output`. To generate more images, run the following commands.

1. Clone the repository and cd into the directory

```
git clone https://github.com/hku-uas/suas-odcl-training-assets.git
cd suas-odcl-training-assets
```

2. Install the required dependencies

```
 pip3 install -r requirements.txt
```

3. Run the script

```
python3 ./src/generate.py [No. of images to generate]
```

---

For generated images of aerial view of cardboard cutouts, they are `{Random ID}.png`s inside `output/`.
For each `.png`, there is a `.json` describing the location and details of the cardboard cutout inside the image.

The `.json` schema is as follows.

```json
{
  "shape_colour": "YELLOW",
  "shape": "PENTAGON",
  "letter_colour": "GREEN",
  "letter": "X",
  "x": 378,
  "y": 150,
  "bbox": [
    366,
    138,
    390,
    162
  ],
  "rot": 72.90281663812398
}
```

- `x` and `y` are coordinates of the cardboard cutout. `bbox` is the bounding box (left, top, right, bottom) and `rot`
  is the rotation in degrees.

![Reference](https://cdn.tutsplus.com/cdn-cgi/image/width=360/net/uploads/legacy/916_canvas1/1.jpg)

- `shape` is the shape of the cardboard cutout. Valid shapes are:

```
CIRCLE,
SEMICIRCLE,
QUARTER_CIRCLE,
TRIANGLE,
SQUARE,
RECTANGLE,
TRAPEZOID,
PENTAGON,
HEXAGON,
HEPTAGON,
OCTAGON,
STAR,
CROSS
```

- `letter` is the letter on the cardboard cutout. Valid letters are:

```
A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z
```

- `shape_colour` and `letter_colour` are the shape background colour and the letter colour respectively. Valid colours
  are:

```
WHITE,
BLACK,
GRAY,
RED,
BLUE,
GREEN,
YELLOW,
PURPLE,
BROWN,
ORANGE
```