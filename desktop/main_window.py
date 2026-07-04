"""
Main window for AirControl desktop application.
"""

from PySide6.QtCore import Qt, QThread, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget

from desktop.camera_thread import CameraWorker
from desktop.camera_widget import CameraWidget
from desktop.control_panel import ControlPanel
from desktop.qt_theme import desktop_theme
from desktop.status_bar import StatusBar
from desktop.status_panel import StatusPanel
from desktop.widgets import HeaderBar, NotificationManager


class MainWindow(QMainWindow):
    """Main application window for AirControl."""

    def __init__(self) -> None:
        super().__init__()
        self._camera_connected = False
        self._tracking_active = False
        self.setup_ui()
        self.setup_camera_thread()
        self._apply_initial_settings()

    def setup_ui(self) -> None:
        """Build the premium desktop layout."""
        self.setWindowTitle("AirControl")
        self.setMinimumSize(1280, 820)
        self.setStyleSheet(desktop_theme.global_stylesheet())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(
            desktop_theme.spacing.window_margin,
            desktop_theme.spacing.window_margin,
            desktop_theme.spacing.window_margin,
            desktop_theme.spacing.window_margin,
        )
        root_layout.setSpacing(desktop_theme.spacing.panel_gap)

        self.header = HeaderBar()
        root_layout.addWidget(self.header)

        body_splitter = QSplitter(Qt.Horizontal)
        root_layout.addWidget(body_splitter, 1)

        self.camera_widget = CameraWidget()
        body_splitter.addWidget(self.camera_widget)
        body_splitter.setStretchFactor(0, 7)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(desktop_theme.spacing.panel_gap)

        self.status_panel = StatusPanel()
        self.control_panel = ControlPanel()
        right_layout.addWidget(self.status_panel, 3)
        right_layout.addWidget(self.control_panel, 2)

        body_splitter.addWidget(right_panel)
        body_splitter.setStretchFactor(1, 3)
        body_splitter.setSizes([860, 360])

        self.notifications = NotificationManager()
        self.notifications.setMinimumHeight(72)
        root_layout.addWidget(self.notifications)

        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

    def setup_camera_thread(self) -> None:
        """Setup the camera processing thread and signal wiring."""
        self.camera_worker = CameraWorker()
        self.camera_thread = QThread()
        self.camera_worker.moveToThread(self.camera_thread)

        self.camera_thread.started.connect(self.camera_worker.start)
        self.camera_thread.finished.connect(self.camera_worker.cleanup)

        self.camera_worker.frame_ready.connect(self.on_frame_ready)
        self.camera_worker.fps_changed.connect(self.status_panel.update_fps)
        self.camera_worker.mode_changed.connect(self.on_mode_changed)
        self.camera_worker.gesture_changed.connect(self.status_panel.update_gesture)
        self.camera_worker.tracking_changed.connect(self.on_tracking_changed)
        self.camera_worker.camera_state_changed.connect(self.on_camera_state_changed)
        self.camera_worker.status_message.connect(self.on_status_message)
        self.camera_worker.action_changed.connect(self.status_panel.update_action)

        # Cursor Speed slider → worker speed multiplier (real-time)
        self.control_panel.speed_changed.connect(self.camera_worker.set_cursor_speed)
        # Cursor Smoothness slider → worker smoothing factor (real-time)
        self.control_panel.smoothing_changed.connect(self.camera_worker.set_smoothing_factor)

        self.control_panel.mirror_changed.connect(self.camera_worker.set_mirror_enabled)
        self.control_panel.left_handed_changed.connect(self.camera_worker.set_left_handed)
        self.control_panel.thresholds_changed.connect(self.camera_worker.set_gesture_thresholds)
        self.control_panel.theme_changed.connect(self.on_theme_changed)

        self.camera_thread.start()

        self.process_timer = QTimer(self)
        self.process_timer.timeout.connect(self.camera_worker.process_frame)
        self.process_timer.start(16)

    def _apply_initial_settings(self) -> None:
        """Push current control panel values to the worker thread at startup.

        Deferred via QTimer.singleShot(0) so the worker is fully initialised
        on its thread before receiving the first slot calls.
        """
        QTimer.singleShot(0, lambda: self.camera_worker.set_cursor_speed(
            self.control_panel.get_cursor_speed()
        ))
        QTimer.singleShot(0, lambda: self.camera_worker.set_smoothing_factor(
            self.control_panel.get_smoothing()
        ))
        QTimer.singleShot(0, lambda: self.camera_worker.set_mirror_enabled(
            self.control_panel.is_mirrored()
        ))
        QTimer.singleShot(0, lambda: self.camera_worker.set_left_handed(
            self.control_panel.is_left_handed()
        ))
        QTimer.singleShot(0, lambda: self.camera_worker.set_gesture_thresholds(
            self.control_panel.get_click_threshold(),
            self.control_panel.get_drag_threshold(),
        ))

    # ------------------------------------------------------------------
    # Slot handlers
    # ------------------------------------------------------------------

    def on_frame_ready(
        self,
        frame,
        fps,
        mode,
        gesture,
        has_pointer,
        has_anchor,
        status_data,
    ) -> None:
        """Handle new frame from camera thread."""
        self.camera_widget.update_frame(frame, mode, gesture, status_data)

        hand_count = int(status_data.get("has_pointer", False)) + int(
            status_data.get("has_anchor", False)
        )
        self.status_panel.update_hands(hand_count)

        frame_size = status_data.get("frame_size")
        if frame_size:
            self.status_bar.set_resolution(frame_size[0], frame_size[1])

    def on_mode_changed(self, mode: str) -> None:
        """Handle mode change."""
        self.status_panel.update_mode(mode)

    def on_tracking_changed(self, tracking: bool) -> None:
        """Handle tracking status change."""
        self._tracking_active = tracking
        self.status_panel.update_tracking(tracking)
        self.header.set_connection(self._camera_connected, tracking)

    def on_camera_state_changed(self, connected: bool) -> None:
        """Handle camera connection state."""
        self._camera_connected = connected
        self.status_panel.update_camera(connected)
        self.header.set_connection(connected, self._tracking_active)

    def on_status_message(self, message: str) -> None:
        """Handle status and toast messages."""
        self.status_bar.set_status(message)
        toast_triggers = (
            "Enabled",
            "Tracking lost",
            "Camera connected",
            "Camera lost",
            "Click",
        )
        if any(token in message for token in toast_triggers):
            self.notifications.show_toast(message)

    def on_theme_changed(self, theme_name: str) -> None:
        """Apply selected desktop theme variant."""
        variant = "classic" if theme_name == "Classic Dark" else "neon"
        stylesheet = desktop_theme.global_stylesheet(variant)
        QApplication.instance().setStyleSheet(stylesheet)
        self.setStyleSheet(stylesheet)
        self.notifications.show_toast(f"Theme: {theme_name}")

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        self.process_timer.stop()
        self.camera_worker.stop()
        self.camera_thread.quit()
        self.camera_thread.wait(3000)
        event.accept()
