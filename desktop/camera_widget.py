"""
Camera widget for displaying the camera feed in the desktop application.
Renders only camera content: hands, cursor, and virtual keyboard.
"""

from typing import Optional

import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from desktop.widgets import AnimatedBorderFrame
from ui.keyboard_ui import KeyboardUI
from ui.renderer_simple import SimpleRenderer


class CameraWidget(QWidget):
    """Widget that displays the camera feed with hand rendering and keyboard."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.renderer = SimpleRenderer()
        self.keyboard = KeyboardUI()

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self.frame_container = AnimatedBorderFrame()
        outer_layout.addWidget(self.frame_container, 1)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(320, 240)
        self.image_label.setStyleSheet("background-color: transparent;")
        self.frame_container.content_layout.addWidget(self.image_label)

        self._display_frame: Optional[np.ndarray] = None
        self._last_params: Optional[tuple] = None

    def update_frame(
        self,
        frame: np.ndarray,
        mode: str,
        gesture: str,
        status_data: dict,
    ) -> None:
        """Update the displayed frame with vision overlays only."""
        render_frame = frame.copy()
        self._last_params = (frame, mode, gesture, status_data)

        # Draw the 60% active tracking area box when in MOUSE mode
        if mode == "MOUSE":
            h, w, _ = render_frame.shape
            margin_x = int(w * 0.2)
            margin_y = int(h * 0.2)
            cv2.rectangle(
                render_frame,
                (margin_x, margin_y),
                (w - margin_x, h - margin_y),
                (246, 130, 59),  # primary blue color (BGR)
                2
            )
            cv2.putText(
                render_frame,
                "Mouse Window (60%)",
                (margin_x + 5, margin_y + 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (246, 130, 59),
                1
            )

        if status_data.get("hands"):
            for hand in status_data["hands"]:
                self.renderer.draw_hand(render_frame, hand.landmarks, hand.label)

        if mode == "KEYBOARD":
            self.keyboard.hovered_key = status_data.get("hovered_key")
            render_frame = self.keyboard.draw(
                render_frame,
                visible=True,
                renderer=self.renderer,
            )

        if status_data.get("has_pointer") and status_data.get("pointer_pos"):
            pointer_pos = status_data["pointer_pos"]
            is_pinching = gesture in ["LEFT_CLICK", "DRAGGING", "DRAG_START"]
            self.renderer.draw_cursor(render_frame, pointer_pos, is_pinching)

        self._update_border_state(status_data)
        self._display_frame = render_frame
        self._paint_frame(render_frame)

    def _update_border_state(self, status_data: dict) -> None:
        """Map runtime state to animated camera border colors."""
        if not status_data.get("camera_connected", True):
            self.frame_container.set_border_state(AnimatedBorderFrame.STATE_LOST)
        elif status_data.get("has_pointer"):
            self.frame_container.set_border_state(AnimatedBorderFrame.STATE_TRACKING)
        elif status_data.get("hands"):
            self.frame_container.set_border_state(AnimatedBorderFrame.STATE_SEARCHING)
        else:
            self.frame_container.set_border_state(AnimatedBorderFrame.STATE_IDLE)

    def _paint_frame(self, frame: np.ndarray) -> None:
        """Convert an OpenCV frame to a pixmap and display it."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame = np.ascontiguousarray(rgb_frame)

        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(
            rgb_frame.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888,
        ).copy()

        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event) -> None:
        """Re-render the last frame when the widget is resized."""
        super().resizeEvent(event)
        if self._display_frame is not None:
            self._paint_frame(self._display_frame)
        elif self._last_params is not None:
            frame, mode, gesture, status_data = self._last_params
            self.update_frame(frame, mode, gesture, status_data)
