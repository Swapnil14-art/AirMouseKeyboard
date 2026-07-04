import cv2
import numpy as np
import time

from vision.camera import Camera
from vision.hand_tracker import HandTracker
from controllers.mouse_controller import MouseController
from gestures.gesture_detector import GestureDetector
from gestures.gesture_types import Gesture
from utils.smoothing import MouseSmoother
from events.event_dispatcher import EventDispatcher
from vision.finger_detector import FingerDetector
from ui.keyboard_ui import KeyboardUI
from controllers.keyboard_controller import KeyboardController
from vision.hand_manager import HandManager
from vision.fist_detector import FistDetector
from managers.mode_manager import ModeManager
from ui.renderer import UIRenderer


from config import *

class AirControlApp:

    def __init__(self):
        self.camera = Camera()
        self.tracker = HandTracker()
        self.mouse = MouseController()
        self.gesture = GestureDetector()
        self.dispatcher = EventDispatcher(self.mouse)
        self.finger_detector = FingerDetector()
        self.mouse_smoother = MouseSmoother(factor=SMOOTHING)
        self.keyboard = KeyboardUI()
        self.keyboard_controller = KeyboardController()
        self.hand_manager = HandManager()
        self.fist_detector = FistDetector(hold_duration_frames=10)  # ~0.17 seconds at 60fps
        self.mode_manager = ModeManager()
        self.renderer = UIRenderer()
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0

    def run(self):
        while True:
            frame = self.camera.get_frame()

            if frame is None:
                break

            frame, hands = self.tracker.process(frame, mirror=self.camera.mirror if self.camera else True)
            self.hand_manager.update(hands)
            
            # Draw custom hand rendering for all detected hands
            for hand in hands:
                frame = self.renderer.draw_hand(frame, hand.landmarks, hand.label)

            # Calculate FPS
            self.fps_counter += 1
            elapsed = time.time() - self.fps_start_time
            if elapsed >= 1.0:
                self.current_fps = self.fps_counter / elapsed
                self.fps_counter = 0
                self.fps_start_time = time.time()

            # Mode Management
            if self.hand_manager.has_two_hands():
                # Check if anchor hand is making a fist to activate keyboard mode
                anchor_fingers = self.finger_detector.get_fingers(
                    self.hand_manager.anchor_hand.landmarks,
                    label=self.hand_manager.anchor_hand.label
                )
                fist_state = self.fist_detector.detect(anchor_fingers)
                
                if self.fist_detector.is_fist_confirmed():
                    self.mode_manager.set_keyboard_mode()
                else:
                    self.mode_manager.set_mouse_mode()
            else:
                # Single hand always in mouse mode
                self.mode_manager.set_mouse_mode()
                self.fist_detector.reset()

            if self.hand_manager.has_pointer():
                # Pointer Finger
                pointer = self.hand_manager.pointer_hand.landmarks[POINTER_FINGER]
                _, x, y = pointer
                camera_x = x
                camera_y = y

                # Only check keyboard hover in keyboard mode
                if self.mode_manager.is_keyboard_mode():
                    self.keyboard.hovered_key = self.keyboard.get_hovered_key(camera_x, camera_y)
                else:
                    self.keyboard.hovered_key = None
                
                h, w, _ = frame.shape

                # Only draw tracking rectangle and move mouse in Mouse Mode
                if self.mode_manager.is_mouse_mode():
                    margin_x = int(w * 0.20)
                    margin_y = int(h * 0.20)
                    # Draw Active Area using renderer
                    self.renderer.draw_active_area(frame, margin_x, margin_y)

                    # Map camera coordinates to screen
                    mapped_x = np.clip(
                        np.interp(
                            x,
                            (margin_x, w - margin_x),
                            (0, self.mouse.screen_width)
                        ),
                        0,
                        self.mouse.screen_width
                    )

                    mapped_y = np.clip(
                        np.interp(
                            y,
                            (margin_y, h - margin_y),
                            (0, self.mouse.screen_height)
                        ),
                        0,
                        self.mouse.screen_height
                    )

                    # Move Cursor with smoothing
                    smooth_x, smooth_y = self.mouse_smoother.smooth(mapped_x, mapped_y)
                    self.mouse.move(smooth_x, smooth_y)

                # Detect Gesture on pointer hand
                fingers = self.finger_detector.get_fingers(
                    self.hand_manager.pointer_hand.landmarks,
                    label=self.hand_manager.pointer_hand.label
                )
                current_gesture = self.gesture.detect(self.hand_manager.pointer_hand.landmarks)
                
                # Handle keyboard input in Keyboard Mode
                if self.mode_manager.is_keyboard_mode():
                    if (
                        current_gesture == Gesture.LEFT_CLICK
                        and self.keyboard.hovered_key is not None
                    ):
                        self.keyboard_controller.press(self.keyboard.hovered_key)
                # Handle mouse gestures in Mouse Mode
                elif self.mode_manager.is_mouse_mode():
                    if self.keyboard.hovered_key is None:
                        self.dispatcher.dispatch(current_gesture)

                # Draw all UI elements using renderer
                is_dragging = current_gesture in [Gesture.DRAGGING, Gesture.DRAG_START, Gesture.DRAG_END]
                frame = self.renderer.draw_all(
                    frame,
                    fps=self.current_fps if self.current_fps > 0 else 30,
                    mode=self.mode_manager.get_mode(),
                    gesture=current_gesture,
                    has_pointer=self.hand_manager.has_pointer(),
                    has_anchor=self.hand_manager.has_anchor(),
                    pointer_pos=(x, y) if self.hand_manager.has_pointer() else None,
                    fingers=fingers,
                    is_dragging=is_dragging,
                    hovered_key=self.keyboard.hovered_key
                )
            
            # Draw Keyboard (only visible if in keyboard mode) using renderer
            frame = self.keyboard.draw(frame, visible=self.mode_manager.is_keyboard_mode(), renderer=self.renderer)
            
            cv2.imshow("AirControl", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.camera.release()
        cv2.destroyAllWindows()