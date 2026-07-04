"""
Reusable premium Qt widgets for AirControl desktop UI.
"""

from typing import Optional

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPainter, QPen, QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)

from desktop.qt_animations import AnimationManager
from desktop.qt_theme import desktop_theme


class StatusCard(QFrame):
    """Glass-style card displaying a single live status metric."""

    def __init__(
        self,
        title: str,
        value: str = "—",
        icon: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._accent = desktop_theme.colors.primary
        self.setObjectName("StatusCard")

        # Allow the card to grow/shrink in both directions so the grid
        # distributes available space evenly and tiles never overlap.
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(60)
        self.setMinimumWidth(90)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            desktop_theme.spacing.card_padding,
            8,
            desktop_theme.spacing.card_padding,
            8,
        )
        layout.setSpacing(4)

        header = QHBoxLayout()
        header.setSpacing(6)

        self.icon_label = QLabel(icon)
        self.icon_label.setVisible(bool(icon))
        self.icon_label.setStyleSheet("font-size: 14px; background: transparent;")
        header.addWidget(self.icon_label)

        self.title_label = QLabel(title.upper())
        self.title_label.setStyleSheet(
            f"color: {desktop_theme.colors.text_muted}; "
            f"font-size: {desktop_theme.fonts.small_size}px; "
            f"font-weight: 600; letter-spacing: 0.8px; background: transparent;"
        )
        header.addWidget(self.title_label)
        header.addStretch()
        layout.addLayout(header)

        self.value_label = QLabel(value)
        self.value_label.setFont(
            QFont(desktop_theme.fonts.family, desktop_theme.fonts.card_value_size, QFont.DemiBold)
        )
        self.value_label.setStyleSheet(
            f"color: {desktop_theme.colors.text_primary}; background: transparent;"
        )
        self.value_label.setWordWrap(True)
        layout.addWidget(self.value_label)
        layout.addStretch(1)

        self._apply_style()

    def _apply_style(self) -> None:
        c = desktop_theme.colors
        s = desktop_theme.spacing
        self.setStyleSheet(
            f"""
            QFrame#StatusCard {{
                background-color: {c.glass};
                border: 1px solid {c.glass_border};
                border-radius: {s.card_radius}px;
            }}
            QFrame#StatusCard:hover {{
                background-color: {c.background_card_hover};
                border-color: {c.border_active};
            }}
            """
        )

    def set_value(self, value: str, color: Optional[str] = None) -> None:
        """Update the card value with optional accent color."""
        self.value_label.setText(value)
        accent = color or desktop_theme.colors.text_primary
        self.value_label.setStyleSheet(
            f"color: {accent}; background: transparent; font-weight: 600;"
        )

    def set_accent(self, color: str) -> None:
        """Update card border accent on next paint."""
        self._accent = color


class GlassPanel(QFrame):
    """Rounded glass panel container for grouped UI sections."""

    def __init__(self, title: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("GlassPanel")

        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(14, 12, 14, 14)
        self.outer_layout.setSpacing(8)

        if title:
            title_label = QLabel(title)
            title_label.setFont(
                QFont(desktop_theme.fonts.family, desktop_theme.fonts.heading_size, QFont.Bold)
            )
            title_label.setStyleSheet(
                f"color: {desktop_theme.colors.primary_glow}; background: transparent;"
            )
            self.outer_layout.addWidget(title_label)

        # Scroll area so the panel content never clips or overlaps when the
        # window is resized smaller than its natural height.
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll.setStyleSheet("background: transparent; border: none;")

        self.content = QWidget()
        self.content.setObjectName("GlassPanelContent")
        self.content.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(desktop_theme.spacing.card_gap)

        self._scroll.setWidget(self.content)
        self.outer_layout.addWidget(self._scroll, 1)

        c = desktop_theme.colors
        s = desktop_theme.spacing
        self.setStyleSheet(
            f"""
            QFrame#GlassPanel {{
                background-color: {c.glass};
                border: 1px solid {c.glass_border};
                border-radius: {s.card_radius}px;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {c.border};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {c.primary};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            """
        )


class AnimatedBorderFrame(QFrame):
    """
    Camera container with animated border reflecting tracking state.
    Blue = idle, Green = tracking, Orange = searching, Red = camera lost.
    """

    STATE_IDLE = "idle"
    STATE_TRACKING = "tracking"
    STATE_SEARCHING = "searching"
    STATE_LOST = "lost"

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._border_state = self.STATE_IDLE
        self._pulse_phase = 0.0
        self._pulse_animation: Optional[QPropertyAnimation] = None

        self.setObjectName("CameraFrame")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        self.content = QWidget()
        self.content.setObjectName("CameraContent")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content)

        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._tick_pulse)
        self._pulse_timer.start(50)

        self._apply_content_style()

    def _apply_content_style(self) -> None:
        s = desktop_theme.spacing
        self.content.setStyleSheet(
            f"""
            QWidget#CameraContent {{
                background-color: {desktop_theme.colors.background_elevated};
                border-radius: {s.camera_radius - 4}px;
            }}
            """
        )

    def set_border_state(self, state: str) -> None:
        """Update border color state."""
        if state != self._border_state:
            self._border_state = state
            self.update()

    def _tick_pulse(self) -> None:
        """Advance pulse phase for animated border glow."""
        if self._border_state in (self.STATE_TRACKING, self.STATE_SEARCHING):
            self._pulse_phase = (self._pulse_phase + 0.08) % 6.28
            self.update()

    def _state_color(self) -> QColor:
        c = desktop_theme.colors
        mapping = {
            self.STATE_IDLE: c.camera_idle,
            self.STATE_TRACKING: c.camera_tracking,
            self.STATE_SEARCHING: c.camera_searching,
            self.STATE_LOST: c.camera_lost,
        }
        return QColor(mapping.get(self._border_state, c.camera_idle))

    def paintEvent(self, event) -> None:
        """Draw rounded frame with glow border."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(2, 2, -2, -2)
        radius = desktop_theme.spacing.camera_radius
        base_color = self._state_color()

        pulse = 0.5 + 0.5 * __import__("math").sin(self._pulse_phase)
        glow_alpha = int(40 + 35 * pulse) if self._border_state != self.STATE_IDLE else 30
        border_width = 3 if self._border_state == self.STATE_TRACKING else 2

        glow = QColor(base_color)
        glow.setAlpha(glow_alpha)
        glow_pen = QPen(glow, border_width + 4)
        glow_pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(glow_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect, radius, radius)

        border_pen = QPen(base_color, border_width)
        border_pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(border_pen)
        painter.drawRoundedRect(rect, radius, radius)
        painter.end()


class ToastWidget(QFrame):
    """Single toast notification with gradient accent."""

    def __init__(self, message: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("Toast")
        self.setFixedHeight(desktop_theme.spacing.toast_height)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)

        dot = QLabel("●")
        dot.setStyleSheet(f"color: {desktop_theme.colors.primary_glow}; font-size: 10px;")
        layout.addWidget(dot)

        label = QLabel(message)
        label.setStyleSheet(
            f"color: {desktop_theme.colors.text_primary}; "
            f"font-size: {desktop_theme.fonts.body_size}px; font-weight: 500;"
        )
        layout.addWidget(label)
        layout.addStretch()

        c = desktop_theme.colors
        self.setStyleSheet(
            f"""
            QFrame#Toast {{
                background-color: {c.background_card};
                border: 1px solid {c.border_active};
                border-radius: 10px;
            }}
            """
        )


class NotificationManager(QWidget):
    """Bottom notification strip with animated toast messages."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("NotificationArea")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(desktop_theme.spacing.toast_gap)
        self.layout.addStretch()

        self._recent_messages: list[str] = []

        c = desktop_theme.colors
        self.setStyleSheet(
            f"""
            QWidget#NotificationArea {{
                background-color: {c.background_elevated};
                border: 1px solid {c.border};
                border-radius: {desktop_theme.spacing.card_radius}px;
            }}
            """
        )

    def show_toast(self, message: str) -> None:
        """Display an auto-dismissing toast notification."""
        if not message or message in self._recent_messages[-3:]:
            return

        self._recent_messages.append(message)
        if len(self._recent_messages) > 12:
            self._recent_messages.pop(0)

        toast = ToastWidget(message, self)
        insert_index = max(self.layout.count() - 1, 0)
        self.layout.insertWidget(insert_index, toast)

        enter = AnimationManager.toast_enter(toast)
        enter.start()

        def dismiss() -> None:
            exit_anim = AnimationManager.fade_out(toast, desktop_theme.animation.fast)
            exit_anim.finished.connect(lambda: self._remove_toast(toast))
            exit_anim.start()

        QTimer.singleShot(desktop_theme.animation.toast_duration, dismiss)

    def _remove_toast(self, toast: ToastWidget) -> None:
        self.layout.removeWidget(toast)
        toast.deleteLater()


class HeaderBar(QWidget):
    """Top application header with title and connection indicator."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(desktop_theme.spacing.header_height)
        self.setObjectName("HeaderBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)

        title = QLabel("AirControl")
        title.setFont(QFont(desktop_theme.fonts.family, desktop_theme.fonts.title_size, QFont.Bold))
        title.setStyleSheet(
            f"color: {desktop_theme.colors.text_primary}; background: transparent;"
        )
        layout.addWidget(title)
        layout.addStretch()

        self.connection_label = QLabel("● Initializing")
        self.connection_label.setStyleSheet(
            f"color: {desktop_theme.colors.text_muted}; "
            f"font-size: {desktop_theme.fonts.body_size}px; font-weight: 600;"
        )
        layout.addWidget(self.connection_label)

        c = desktop_theme.colors
        self.setStyleSheet(
            f"""
            QWidget#HeaderBar {{
                background-color: {c.background_elevated};
                border: 1px solid {c.border};
                border-radius: {desktop_theme.spacing.card_radius}px;
            }}
            """
        )

    def set_connection(self, camera: bool, tracking: bool) -> None:
        """Update the header connection indicator."""
        c = desktop_theme.colors
        if tracking:
            text = "● Tracking"
            color = c.success
        elif camera:
            text = "● Camera Ready"
            color = c.primary_glow
        else:
            text = "● No Camera"
            color = c.danger
        self.connection_label.setText(text)
        self.connection_label.setStyleSheet(
            f"color: {color}; font-size: {desktop_theme.fonts.body_size}px; font-weight: 600;"
        )
