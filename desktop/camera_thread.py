"""
Camera processing worker for AirControl desktop application.
Handles camera capture and vision processing on a worker thread.
"""

import time
from typing import Optional

import numpy as np
from PySide6.QtCore import QObject, Signal, Slot

import config
from controllers.keyboard_controller import KeyboardController
from controllers.mouse_controller import MouseController
from events.event_dispatcher import EventDispatcher
from gestures.gesture_detector import GestureDetector
from gestures.gesture_types import Gesture
from managers.mode_manager import ModeManager
from ui.keyboard_ui import KeyboardUI
from utils.smoothing import MouseSmoother
from vision.camera import Camera
from vision.finger_detector import FingerDetector
from vision.fist_detector import FistDetector
from vision.hand_manager import HandManager
from vision.hand_tracker import HandTracker

from config import FRAME_MARGIN_X, FRAME_MARGIN_Y, POINTER_FINGER, SMOOTHING

# Default cursor speed level (1–10).  Maps to a linear multiplier so the
# user perceives a proportional change in how far the cursor travels per
# unit of hand movement.
_DEFAULT_SPEED = 5
_SPEED_SCALE = 0.2   # multiplier = speed_level * _SPEED_SCALE  (5 → 1.0×)


class CameraWorker(QObject):
    """Processes camera frames and emits UI/controller updates via Qt signals."""

    frame_ready = Signal(np.ndarray, float, str, str, bool, bool, dict)
    fps_changed = Signal(float)
    mode_changed = Signal(str)
    gesture_changed = Signal(str)
    tracking_changed = Signal(bool)
    camera_state_changed = Signal(bool)
    status_message = Signal(str)
    action_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.running = False
        self.paused = False
        self._initialized = False
        self._camera_connected = False

        # Cursor speed multiplier (runtime-adjustable via set_cursor_speed).
        # Default level 5 → multiplier 1.0 (no change to existing behaviour).
        self._cursor_speed_multiplier: float = _DEFAULT_SPEED * _SPEED_SCALE

        self.camera: Optional[Camera] = None
        self.tracker: Optional[HandTracker] = None
        self.mouse: Optional[MouseController] = None
        self.gesture: Optional[GestureDetector] = None
        self.dispatcher: Optional[EventDispatcher] = None
        self.finger_detector: Optional[FingerDetector] = None
        self.mouse_smoother: Optional[MouseSmoother] = None
        self.keyboard: Optional[KeyboardUI] = None
        self.keyboard_controller: Optional[KeyboardController] = None
        self.hand_manager: Optional[HandManager] = None
        self.fist_detector: Optional[FistDetector] = None
        self.mode_manager: Optional[ModeManager] = None

        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0.0

        self._last_mode = "MOUSE"
        self._last_gesture = "Idle"
        self._last_tracking = False
        self._last_action = "Idle"
        self._frame_failures = 0

    def start(self) -> None:
        """Initialize components on the worker thread and begin processing."""
        self.status_message.emit("Camera starting...")

        if not self._initialized:
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
            self.fist_detector = FistDetector(hold_duration_frames=10)
            self.mode_manager = ModeManager()
            self._initialized = True

        self.running = True
        self.paused = False
        self.fps_start_time = time.time()
        self._camera_connected = self.camera.is_opened()
        self.camera_state_changed.emit(self._camera_connected)

        if self._camera_connected:
            self.status_message.emit("Camera connected")
        else:
            self.status_message.emit("Camera not detected")

    def stop(self) -> None:
        """Stop frame processing."""
        self.running = False
        self.status_message.emit("Camera stopped")

    def pause(self) -> None:
        """Pause frame processing."""
        self.paused = True
        self.status_message.emit("Camera paused")

    def resume(self) -> None:
        """Resume frame processing."""
        self.paused = False
        self.status_message.emit("Camera resumed")

    # ------------------------------------------------------------------
    # Runtime-adjustable slots
    # ------------------------------------------------------------------

    @Slot(int)
    def set_cursor_speed(self, level: int) -> None:
        """Update cursor speed from a 1–10 slider value.

        The level is converted to a linear multiplier:
          level 1  → 0.2×  (very slow)
          level 5  → 1.0×  (default — identical to previous behaviour)
          level 10 → 2.0×  (very fast)

        The multiplier is applied to the *offset from screen centre* so that
        the cursor always reaches the edges regardless of speed setting; it
        simply arrives there with less/more hand movement.
        """
        self._cursor_speed_multiplier = max(int(level), 1) * _SPEED_SCALE

    @Slot(int)
    def set_smoothing_factor(self, factor: int) -> None:
        """Update mouse smoothing factor (1 = raw, 20 = very smooth)."""
        if self.mouse_smoother is not None:
            self.mouse_smoother.set_factor(factor)

    @Slot(bool)
    def set_mirror_enabled(self, enabled: bool) -> None:
        """Toggle camera mirroring."""
        if self.camera is not None:
            self.camera.set_mirror(enabled)

    @Slot(bool)
    def set_left_handed(self, left_handed: bool) -> None:
        """Toggle left-handed hand assignment."""
        if self.hand_manager is not None:
            self.hand_manager.set_handedness(left_handed)

    @Slot(int, int)
    def set_gesture_thresholds(self, click_distance: int, drag_distance: int) -> None:
        """Update gesture distance thresholds at runtime."""
        config.LEFT_CLICK_DISTANCE = click_distance
        config.RIGHT_CLICK_DISTANCE = click_distance
        config.DRAG_DISTANCE = drag_distance

    # ------------------------------------------------------------------
    # Frame processing
    # ------------------------------------------------------------------

    def process_frame(self) -> None:
        """Process a single camera frame."""
        if not self.running or self.paused or not self._initialized:
            return

        frame = self.camera.get_frame()
        if frame is None:
            self._frame_failures += 1
            if self._frame_failures >= 5 and self._camera_connected:
                self._camera_connected = False
                self.camera_state_changed.emit(False)
                self.tracking_changed.emit(False)
                self._last_tracking = False
                self.status_message.emit("Camera lost")
            return

        self._frame_failures = 0
        if not self._camera_connected:
            self._camera_connected = True
            self.camera_state_changed.emit(True)
            self.status_message.emit("Camera connected")

        frame, hands = self.tracker.process(frame, mirror=self.camera.mirror if self.camera else True)
        self.hand_manager.update(hands)

        self.fps_counter += 1
        elapsed = time.time() - self.fps_start_time
        if elapsed >= 1.0:
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = time.time()
            self.fps_changed.emit(self.current_fps)

        if self.hand_manager.has_two_hands():
            anchor_fingers = self.finger_detector.get_fingers(
                self.hand_manager.anchor_hand.landmarks,
                label=self.hand_manager.anchor_hand.label
            )
            self.fist_detector.detect(anchor_fingers)

            if self.fist_detector.is_fist_confirmed():
                self.mode_manager.set_keyboard_mode()
            else:
                self.mode_manager.set_mouse_mode()
        else:
            self.mode_manager.set_mouse_mode()
            self.fist_detector.reset()

        current_mode = self.mode_manager.get_mode().value
        if current_mode != self._last_mode:
            self._last_mode = current_mode
            self.mode_changed.emit(current_mode)
            label = "Keyboard Mode Enabled" if current_mode == "KEYBOARD" else "Mouse Mode Enabled"
            self.status_message.emit(label)

        pointer_pos = None
        fingers = None
        current_gesture = Gesture.NONE
        is_dragging = False
        hovered_key = None
        click_state = "Idle"
        action = "Idle"

        if self.hand_manager.has_pointer():
            pointer = self.hand_manager.pointer_hand.landmarks[POINTER_FINGER]
            _, x, y = pointer
            pointer_pos = (x, y)

            if self.mode_manager.is_keyboard_mode():
                self.keyboard.hovered_key = self.keyboard.get_hovered_key(x, y)
                hovered_key = self.keyboard.hovered_key
            else:
                self.keyboard.hovered_key = None

            h, w, _ = frame.shape

            if self.mode_manager.is_mouse_mode():
                # Map camera coordinates into screen space using 60% center window.
                margin_x = int(w * 0.20)
                margin_y = int(h * 0.20)
                mapped_x = np.clip(
                    np.interp(
                        x,
                        (margin_x, w - margin_x),
                        (0, self.mouse.screen_width),
                    ),
                    0,
                    self.mouse.screen_width,
                )
                mapped_y = np.clip(
                    np.interp(
                        y,
                        (margin_y, h - margin_y),
                        (0, self.mouse.screen_height),
                    ),
                    0,
                    self.mouse.screen_height,
                )

                # Apply cursor speed multiplier around the screen centre.
                # Scaling about the centre means the cursor always reaches
                # the edges with enough hand movement, but arrives there
                # faster (or slower) depending on the speed setting.
                cx = self.mouse.screen_width / 2
                cy = self.mouse.screen_height / 2
                spd = self._cursor_speed_multiplier
                scaled_x = np.clip(cx + (mapped_x - cx) * spd, 0, self.mouse.screen_width)
                scaled_y = np.clip(cy + (mapped_y - cy) * spd, 0, self.mouse.screen_height)

                smooth_x, smooth_y = self.mouse_smoother.smooth(scaled_x, scaled_y)
                self.mouse.move(smooth_x, smooth_y)

            fingers = self.finger_detector.get_fingers(
                self.hand_manager.pointer_hand.landmarks,
                label=self.hand_manager.pointer_hand.label
            )
            current_gesture = self.gesture.detect(
                self.hand_manager.pointer_hand.landmarks
            )

            if self.mode_manager.is_keyboard_mode():
                if current_gesture == Gesture.LEFT_CLICK and self.keyboard.hovered_key is not None:
                    self.keyboard_controller.press(self.keyboard.hovered_key)
                    click_state = f"Pressed: {self.keyboard.hovered_key}"
                    action = f"Key {self.keyboard.hovered_key}"
            elif self.mode_manager.is_mouse_mode():
                self.dispatcher.dispatch(current_gesture)

                if current_gesture == Gesture.LEFT_CLICK:
                    click_state = "Left Click"
                    action = "Left Click"
                elif current_gesture == Gesture.RIGHT_CLICK:
                    click_state = "Right Click"
                    action = "Right Click"
                elif current_gesture == Gesture.DRAGGING:
                    click_state = "Dragging"
                    action = "Dragging"
                elif current_gesture == Gesture.DRAG_START:
                    click_state = "Drag Start"
                    action = "Drag Start"
                elif current_gesture == Gesture.DRAG_END:
                    click_state = "Drag End"
                    action = "Drag End"

            is_dragging = current_gesture in [
                Gesture.DRAGGING,
                Gesture.DRAG_START,
                Gesture.DRAG_END,
            ]

        gesture_name = current_gesture.name if current_gesture != Gesture.NONE else "Idle"
        if gesture_name != self._last_gesture:
            self._last_gesture = gesture_name
            self.gesture_changed.emit(gesture_name)

        if action != self._last_action:
            self._last_action = action
            self.action_changed.emit(action)

        tracking_active = self.hand_manager.has_pointer()
        if tracking_active != self._last_tracking:
            self._last_tracking = tracking_active
            self.tracking_changed.emit(tracking_active)
            if not tracking_active:
                self.status_message.emit("Tracking lost")

        status_data = {
            "gesture": gesture_name,
            "click_state": click_state,
            "action": action,
            "fingers": fingers,
            "hovered_key": hovered_key,
            "is_dragging": is_dragging,
            "has_pointer": self.hand_manager.has_pointer(),
            "has_anchor": self.hand_manager.has_anchor(),
            "pointer_pos": pointer_pos,
            "hands": hands,
            "camera_connected": self._camera_connected,
            "frame_size": (frame.shape[1], frame.shape[0]),
        }

        self.frame_ready.emit(
            frame,
            self.current_fps if self.current_fps > 0 else 30.0,
            current_mode,
            gesture_name,
            self.hand_manager.has_pointer(),
            self.hand_manager.has_anchor(),
            status_data,
        )

    def cleanup(self) -> None:
        """Release camera and vision resources."""
        if self.camera is not None:
            self.camera.release()
