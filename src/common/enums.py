from enum import Enum, IntEnum


class SuasColour(Enum):
    WHITE = "#F3F7FD"
    BLACK = "#22272C"
    GRAY = "#949CA3"
    RED = "#BA0F3C"
    BLUE = "#1B71D3"
    GREEN = "#37905F"
    YELLOW = "#F2D519"
    PURPLE = "#643D98"
    BROWN = "#964B00"
    ORANGE = "#FE8512"


class SuasShape(IntEnum):
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
