from gestures.gesture_types import Gesture


class EventDispatcher:

    def __init__(self, mouse):

        self.mouse = mouse

    def dispatch(self, gesture):

        if gesture == Gesture.LEFT_CLICK:

            self.mouse.left_click()

        elif gesture == Gesture.RIGHT_CLICK:

            self.mouse.right_click()

        elif gesture == Gesture.DRAG_START:

            self.mouse.drag_start()

        elif gesture == Gesture.DRAG_END:

            self.mouse.drag_end()