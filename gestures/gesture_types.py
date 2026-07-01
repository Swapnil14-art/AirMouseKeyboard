from enum import Enum


class Gesture(Enum):

    NONE = 0

    LEFT_CLICK = 1

    RIGHT_CLICK = 2

    DRAG_START = 3

    DRAGGING = 4

    DRAG_END = 5