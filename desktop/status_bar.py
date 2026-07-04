"""
Status bar widget for displaying application status messages.
"""

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QStatusBar

from desktop.qt_theme import desktop_theme


class StatusBar(QStatusBar):
    """Custom status bar for persistent application messages."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._default_message = "Ready"
        self._setup_ui()

    def _setup_ui(self) -> None:
        c = desktop_theme.colors
        self.setStyleSheet(
            f"""
            QStatusBar {{
                background-color: {c.background_elevated};
                color: {c.text_secondary};
                border-top: 1px solid {c.border};
            }}
            """
        )

        self.status_label = QLabel(self._default_message)
        self.status_label.setFont(QFont(desktop_theme.fonts.family, desktop_theme.fonts.small_size))
        self.addWidget(self.status_label, 1)

        self.resolution_label = QLabel("")
        self.resolution_label.setStyleSheet(f"color: {c.text_muted};")
        self.addPermanentWidget(self.resolution_label)

        self._clear_timer = QTimer(self)
        self._clear_timer.setSingleShot(True)
        self._clear_timer.timeout.connect(self._reset_message)

    def set_status(self, message: str, temporary: bool = True) -> None:
        """Set the main status message."""
        self.status_label.setText(message)
        self._clear_timer.stop()
        if temporary and message not in ("Ready", self._default_message):
            self._clear_timer.start(4000)

    def _reset_message(self) -> None:
        self.status_label.setText(self._default_message)

    def set_resolution(self, width: int, height: int) -> None:
        """Set camera resolution display."""
        if width and height:
            self.resolution_label.setText(f"{width}×{height}")
        else:
            self.resolution_label.setText("")

    def show_message(self, message: str, duration: int = 3000) -> None:
        """Show a temporary status message."""
        self.set_status(message, temporary=False)
        self._clear_timer.stop()
        self._clear_timer.start(duration)
