from enum import Enum


class SuasColour(Enum):
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    GRAY = "#808080"
    RED = "#FF0000"
    BLUE = "#0000FF"
    GREEN = "#00FF00"
    YELLOW = "#FFFF00"
    PURPLE = "#800080"
    BROWN = "#A52A2A"
    ORANGE = "#FFA500"


class SuasShape(Enum):
    CIRCLE = 0
    SEMICIRCLE = 1
    QUARTER_CIRCLE = 2
    TRIANGLE = 3
    SQUARE = 4
    RECTANGLE = 5
    TRAPEZOID = 6
    PENTAGON = 7
    HEXAGON = 8
    HEPTAGON = 9
    OCTAGON = 10
    STAR = 11
    CROSS = 12
