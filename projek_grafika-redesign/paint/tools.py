from enum import Enum, auto


class Tool(Enum):

    # ==========================
    # SELECTION
    # ==========================
    SELECT = auto()

    # ==========================
    # DRAWING TOOLS
    # ==========================
    PENCIL = auto()
    BRUSH = auto()
    ERASER = auto()

    # ==========================
    # BASIC SHAPES
    # ==========================
    LINE = auto()

    RECTANGLE = auto()
    ROUNDED_RECTANGLE = auto()

    CIRCLE = auto()
    ELLIPSE = auto()

    TRIANGLE = auto()

    DIAMOND = auto()

    PENTAGON = auto()

    HEXAGON = auto()

    STAR = auto()

    # ==========================
    # ARROWS
    # ==========================
    ARROW_RIGHT = auto()

    ARROW_LEFT = auto()

    ARROW_UP = auto()

    ARROW_DOWN = auto()

    # ==========================
    # ADVANCED
    # ==========================
    CURVE = auto()

    # ==========================
    # UTILITIES
    # ==========================
    FILL = auto()

    TEXT = auto()


class ShapeMode(Enum):

    NONE = auto()

    LINE = auto()

    RECTANGLE = auto()

    ROUNDED_RECTANGLE = auto()

    CIRCLE = auto()

    ELLIPSE = auto()

    TRIANGLE = auto()

    DIAMOND = auto()

    PENTAGON = auto()

    HEXAGON = auto()

    STAR = auto()

    ARROW_RIGHT = auto()

    ARROW_LEFT = auto()

    ARROW_UP = auto()

    ARROW_DOWN = auto()

    CURVE = auto()


class BrushStyle(Enum):

    NORMAL = auto()

    DASHED = auto()

    DOTTED = auto()

    DASH_DOT = auto()

class AnimationType(Enum):

    NONE = auto()

    BOUNCE = auto()

    SPIN = auto()

    PULSE = auto()

TOOL_NAMES = {

    # Selection
    Tool.SELECT:
        "Select",

    # Drawing
    Tool.PENCIL:
        "Pencil",

    Tool.BRUSH:
        "Brush",

    Tool.ERASER:
        "Eraser",

    # Shapes
    Tool.LINE:
        "Line",

    Tool.RECTANGLE:
        "Rectangle",

    Tool.ROUNDED_RECTANGLE:
        "Rounded Rectangle",

    Tool.CIRCLE:
        "Circle",

    Tool.ELLIPSE:
        "Ellipse",

    Tool.TRIANGLE:
        "Triangle",

    Tool.DIAMOND:
        "Diamond",

    Tool.PENTAGON:
        "Pentagon",

    Tool.HEXAGON:
        "Hexagon",

    Tool.STAR:
        "Star",

    Tool.ARROW_RIGHT:
        "Arrow Right",

    Tool.ARROW_LEFT:
        "Arrow Left",

    Tool.ARROW_UP:
        "Arrow Up",

    Tool.ARROW_DOWN:
        "Arrow Down",

    Tool.CURVE:
        "Curve",

    # Utility
    Tool.FILL:
        "Fill",

    Tool.TEXT:
        "Text",
}


# ==========================
# SHAPE TOOLS
# ==========================

SHAPE_TOOLS = [

    Tool.LINE,

    Tool.RECTANGLE,
    Tool.ROUNDED_RECTANGLE,

    Tool.CIRCLE,
    Tool.ELLIPSE,

    Tool.TRIANGLE,

    Tool.DIAMOND,

    Tool.PENTAGON,

    Tool.HEXAGON,

    Tool.STAR,

    Tool.ARROW_RIGHT,
    Tool.ARROW_LEFT,
    Tool.ARROW_UP,
    Tool.ARROW_DOWN,

    Tool.CURVE
]


# ==========================
# DRAWING TOOLS
# ==========================

DRAWING_TOOLS = [

    Tool.PENCIL,

    Tool.BRUSH,

    Tool.ERASER
]


# ==========================
# UTILITY TOOLS
# ==========================

UTILITY_TOOLS = [

    Tool.FILL,

    Tool.TEXT
]