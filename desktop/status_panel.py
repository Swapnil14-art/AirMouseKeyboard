"""
Status panel widget for displaying real-time application status.
"""

from typing import Dict

from PySide6.QtWidgets import QGridLayout, QSizePolicy, QWidget

from desktop.qt_theme import desktop_theme
from desktop.widgets import GlassPanel, StatusCard


class StatusPanel(GlassPanel):
    """Panel displaying live status cards."""

    GESTURE_LABELS = {
        "Idle": ("—", desktop_theme.colors.text_muted),
        "LEFT_CLICK": ("👌 Pinch", desktop_theme.colors.success),
        "RIGHT_CLICK": ("✌ Victory", desktop_theme.colors.warning),
        "DRAG_START": ("✊ Drag Start", desktop_theme.colors.primary_glow),
        "DRAGGING": ("✊ Dragging", desktop_theme.colors.warning),
        "DRAG_END": ("✊ Drag End", desktop_theme.colors.text_secondary),
        "NONE": ("—", desktop_theme.colors.text_muted),
    }

    MODE_LABELS = {
        "MOUSE": ("🖱 Mouse", desktop_theme.colors.primary_glow),
        "KEYBOARD": ("⌨ Keyboard", desktop_theme.colors.success),
    }

    def __init__(self, parent=None) -> None:
        super().__init__("Live Status", parent)
        self.cards: Dict[str, StatusCard] = {}

        # Host widget for the grid — lives inside the scroll area provided
        # by GlassPanel, so cards are never clipped or overlapped.
        grid_host = QWidget()
        grid_host.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        grid = QGridLayout(grid_host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(desktop_theme.spacing.card_gap)

        # Two equal-width columns; rows expand proportionally.
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        card_defs = [
            ("tracking", "Tracking", "🔴 Inactive", "📡"),
            ("fps", "FPS", "0 FPS", "⚡"),
            ("mode", "Mode", "🖱 Mouse", "🎛"),
            ("gesture", "Gesture", "—", "👋"),
            ("action", "Action", "Idle", "🎯"),
            ("hands", "Hands", "0 Detected", "🤚"),
            ("camera", "Camera", "Connecting", "📷"),
        ]

        num_cols = 2
        for index, (key, title, value, icon) in enumerate(card_defs):
            card = StatusCard(title, value, icon)
            self.cards[key] = card
            row, col = divmod(index, num_cols)
            grid.addWidget(card, row, col)

        # Give each row equal stretch so all cards share available height.
        num_rows = -(-len(card_defs) // num_cols)  # ceiling division
        for r in range(num_rows):
            grid.setRowStretch(r, 1)

        self.content_layout.addWidget(grid_host)

    # ------------------------------------------------------------------
    # Update helpers
    # ------------------------------------------------------------------

    def update_tracking(self, active: bool) -> None:
        if active:
            self.cards["tracking"].set_value("🟢 Active", desktop_theme.colors.success)
        else:
            self.cards["tracking"].set_value("🔴 Inactive", desktop_theme.colors.danger)

    def update_fps(self, fps: float) -> None:
        value = f"{int(fps)} FPS"
        if fps >= 28:
            color = desktop_theme.colors.success
        elif fps >= 20:
            color = desktop_theme.colors.warning
        else:
            color = desktop_theme.colors.danger
        self.cards["fps"].set_value(value, color)

    def update_mode(self, mode: str) -> None:
        label, color = self.MODE_LABELS.get(mode, (mode, desktop_theme.colors.text_primary))
        self.cards["mode"].set_value(label, color)

    def update_gesture(self, gesture: str) -> None:
        label, color = self.GESTURE_LABELS.get(
            gesture,
            (gesture.replace("_", " ").title(), desktop_theme.colors.text_primary),
        )
        self.cards["gesture"].set_value(label, color)

    def update_action(self, action: str) -> None:
        if action == "Idle":
            self.cards["action"].set_value("Idle", desktop_theme.colors.text_muted)
        else:
            self.cards["action"].set_value(action, desktop_theme.colors.primary_glow)

    def update_hands(self, count: int) -> None:
        label = f"{count} Detected"
        color = desktop_theme.colors.success if count > 0 else desktop_theme.colors.text_muted
        self.cards["hands"].set_value(label, color)

    def update_camera(self, connected: bool) -> None:
        if connected:
            self.cards["camera"].set_value("Connected", desktop_theme.colors.success)
        else:
            self.cards["camera"].set_value("Disconnected", desktop_theme.colors.danger)
