import math

from gestures.gesture_types import Gesture
from config import *


class GestureDetector:

    def __init__(self):

        self.left_clicked = False
        self.right_clicked = False

        self.dragging = False
        self.drag_counter = 0

    def distance(self, p1, p2):

        _, x1, y1 = p1
        _, x2, y2 = p2

        return math.hypot(x2 - x1, y2 - y1)

    def detect(self, landmarks):
        """Detect mouse-related gestures (clicks, drag)."""
        thumb = landmarks[THUMB_TIP]
        middle = landmarks[MIDDLE_TIP]
        ring = landmarks[RING_TIP]

        thumb_middle = self.distance(thumb, middle)
        thumb_ring = self.distance(thumb, ring)

        # ------------------------
        # DRAG MODE
        # ------------------------

        if thumb_middle < DRAG_DISTANCE:

            self.drag_counter += 1

            if self.drag_counter >= DRAG_START_FRAMES:

                if not self.dragging:

                    self.dragging = True
                    return Gesture.DRAG_START

                return Gesture.DRAGGING

        else:

            self.drag_counter = 0

            if self.dragging:

                self.dragging = False
                return Gesture.DRAG_END

        # ------------------------
        # LEFT CLICK
        # ------------------------

        if thumb_middle < LEFT_CLICK_DISTANCE:

            if not self.left_clicked:

                self.left_clicked = True
                return Gesture.LEFT_CLICK

        else:

            self.left_clicked = False

        # ------------------------
        # RIGHT CLICK
        # ------------------------

        if thumb_ring < RIGHT_CLICK_DISTANCE:

            if not self.right_clicked:

                self.right_clicked = True
                return Gesture.RIGHT_CLICK

        else:

            self.right_clicked = False

        return Gesture.NONE