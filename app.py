# pyrefly: ignore [missing-import]
import cv2
import numpy as np

from vision.camera import Camera
from vision.hand_tracker import HandTracker

from controllers.mouse_controller import MouseController

from gestures.gesture_detector import GestureDetector
from gestures.gesture_types import Gesture
from utils.smoothing import MouseSmoother
from events.event_dispatcher import EventDispatcher
from vision.finger_detector import FingerDetector
from config import *

class AirControlApp:

    def __init__(self):

        self.camera = Camera()
        self.tracker = HandTracker()
        self.mouse = MouseController()
        self.gesture = GestureDetector()
        self.dispatcher = EventDispatcher(self.mouse)
        self.smoother = MouseSmoother()
        self.finger_detector = FingerDetector()

    def run(self):

        while True:

            frame = self.camera.get_frame()

            if frame is None:
                break

            frame, landmarks = self.tracker.process(frame)

            if landmarks:

                # Pointer Finger
                pointer = landmarks[POINTER_FINGER]
                _, x, y = pointer

                h, w, _ = frame.shape

                # Draw Active Area
                cv2.rectangle(
                    frame,
                    (FRAME_MARGIN, FRAME_MARGIN),
                    (w - FRAME_MARGIN, h - FRAME_MARGIN),
                    (255, 0, 255),
                    2
                )

                # Map camera coordinates to screen
                mapped_x = np.clip(
                    np.interp(
                        x,
                        (FRAME_MARGIN, w - FRAME_MARGIN),
                        (0, self.mouse.screen_width)
                    ),
                    0,
                    self.mouse.screen_width
                )

                mapped_y = np.clip(
                    np.interp(
                        y,
                        (FRAME_MARGIN, h - FRAME_MARGIN),
                        (0, self.mouse.screen_height)
                    ),
                    0,
                    self.mouse.screen_height
                )

                # Move Cursor
                smooth_x, smooth_y = self.smoother.smooth(mapped_x, mapped_y)
                self.mouse.move(mapped_x, mapped_y)

                # Detect Gesture
                fingers = self.finger_detector.get_fingers(landmarks)
                current_gesture = self.gesture.detect(landmarks)

                # Perform Action
                self.dispatcher.dispatch(current_gesture)

                # Draw Pointer
                cv2.circle(frame, (x, y), 15, (0, 255, 0), -1)

                # Display Gesture
                cv2.putText(
                    frame,
                    f"Gesture : {current_gesture.name}",
                    (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    frame,
                    f"Fingers : {fingers}",
                    (10,80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255,255,0),
                    2
                )

            cv2.imshow("AirControl", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.camera.release()
        cv2.destroyAllWindows()