"""
Control panel widget for application settings and controls.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from config import DRAG_DISTANCE, LEFT_CLICK_DISTANCE, SMOOTHING
from desktop.qt_theme import desktop_theme
from desktop.widgets import GlassPanel

# Default cursor speed (1–10 scale, maps to a multiplier applied during movement)
DEFAULT_CURSOR_SPEED = 5


class ControlPanel(GlassPanel):
    """Panel containing application controls and settings."""

    # Emitted when the cursor speed multiplier changes (1–10)
    speed_changed = Signal(int)
    # Emitted when the smoothing factor changes (1–20, higher = smoother/slower)
    smoothing_changed = Signal(int)
    mirror_changed = Signal(bool)
    left_handed_changed = Signal(bool)
    thresholds_changed = Signal(int, int)
    theme_changed = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__("Controls", parent)
        self._build_controls()

    def _build_controls(self) -> None:
        c = desktop_theme.colors

        # --- Cursor Speed (1 = slow, 10 = fast) ---
        # This is an independent multiplier applied to mapped coordinates
        # before they are passed to the mouse controller.
        self.speed_slider, self.speed_value_label = self._add_slider(
            "Cursor Speed",
            1,
            10,
            DEFAULT_CURSOR_SPEED,
        )
        self.speed_slider.valueChanged.connect(self._on_speed_changed)

        # --- Cursor Smoothness (1 = raw/no smoothing, 20 = very smooth/slow) ---
        # Directly drives MouseSmoother.factor.  Higher value = more lag
        # compensation frames averaged = smoother but less responsive.
        self.smoothing_slider, self.smoothing_value_label = self._add_slider(
            "Cursor Smoothness",
            1,
            20,
            SMOOTHING,
        )
        self.smoothing_slider.valueChanged.connect(self._on_smoothing_changed)

        # --- Toggles ---
        self.mirror_checkbox = QCheckBox("Mirror Camera")
        self.mirror_checkbox.setChecked(True)
        self.mirror_checkbox.toggled.connect(self.mirror_changed.emit)
        self.content_layout.addWidget(self.mirror_checkbox)

        self.left_handed_checkbox = QCheckBox("Left-Handed Mode")
        self.left_handed_checkbox.setChecked(False)
        self.left_handed_checkbox.toggled.connect(self.left_handed_changed.emit)
        self.content_layout.addWidget(self.left_handed_checkbox)

        # --- Theme selector ---
        theme_row = QHBoxLayout()
        theme_label = QLabel("Theme")
        theme_label.setStyleSheet(f"color: {c.text_secondary};")
        theme_row.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Neon Dark", "Classic Dark"])
        self.theme_combo.setCurrentIndex(0)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        theme_row.addWidget(self.theme_combo)
        self.content_layout.addLayout(theme_row)

        # --- Gesture distance spinboxes ---
        self.click_threshold = self._add_spinbox(
            "Click Distance",
            20,
            60,
            LEFT_CLICK_DISTANCE,
        )
        self.drag_threshold = self._add_spinbox(
            "Drag Distance",
            20,
            50,
            DRAG_DISTANCE,
        )
        self.click_threshold.valueChanged.connect(self._emit_thresholds)
        self.drag_threshold.valueChanged.connect(self._emit_thresholds)

        self.content_layout.addStretch()

        self.setStyleSheet(
            self.styleSheet()
            + f"""
            QCheckBox {{
                color: {c.text_primary};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1px solid {c.border};
                background: {c.background_elevated};
            }}
            QCheckBox::indicator:checked {{
                background: {c.primary};
                border-color: {c.primary_glow};
            }}
            QSlider::groove:horizontal {{
                height: 6px;
                background: {c.slider_groove};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {c.slider_handle};
                width: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QSpinBox, QComboBox {{
                background: {c.background_elevated};
                color: {c.text_primary};
                border: 1px solid {c.border};
                border-radius: 6px;
                padding: 4px 8px;
            }}
            QSpinBox:focus, QComboBox:focus {{
                border-color: {c.primary};
            }}
            """
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _add_slider(
        self,
        label_text: str,
        min_val: int,
        max_val: int,
        default: int,
    ) -> tuple[QSlider, QLabel]:
        row = QVBoxLayout()
        value_label = QLabel(f"{label_text}: {default}")
        value_label.setFont(
            QFont(desktop_theme.fonts.family, desktop_theme.fonts.small_size)
        )
        value_label.setStyleSheet(f"color: {desktop_theme.colors.text_secondary};")
        row.addWidget(value_label)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default)
        slider.valueChanged.connect(
            lambda value: value_label.setText(f"{label_text}: {value}")
        )
        row.addWidget(slider)

        wrapper = QWidget()
        wrapper.setLayout(row)
        self.content_layout.addWidget(wrapper)
        return slider, value_label

    def _add_spinbox(
        self,
        label_text: str,
        min_val: int,
        max_val: int,
        default: int,
    ) -> QSpinBox:
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet(f"color: {desktop_theme.colors.text_secondary};")
        row.addWidget(label)

        spinbox = QSpinBox()
        spinbox.setMinimum(min_val)
        spinbox.setMaximum(max_val)
        spinbox.setValue(default)
        spinbox.setFixedWidth(72)
        row.addWidget(spinbox)
        row.addStretch()

        wrapper = QWidget()
        wrapper.setLayout(row)
        self.content_layout.addWidget(wrapper)
        return spinbox

    # ------------------------------------------------------------------
    # Signal emitters
    # ------------------------------------------------------------------

    def _on_speed_changed(self, value: int) -> None:
        self.speed_changed.emit(value)

    def _on_smoothing_changed(self, value: int) -> None:
        self.smoothing_changed.emit(value)

    def _emit_thresholds(self) -> None:
        self.thresholds_changed.emit(
            self.click_threshold.value(),
            self.drag_threshold.value(),
        )

    def _on_theme_changed(self, theme_name: str) -> None:
        self.theme_changed.emit(theme_name)

    # ------------------------------------------------------------------
    # Accessors (used by MainWindow._apply_initial_settings)
    # ------------------------------------------------------------------

    def get_cursor_speed(self) -> int:
        return self.speed_slider.value()

    def get_smoothing(self) -> int:
        return self.smoothing_slider.value()

    def is_mirrored(self) -> bool:
        return self.mirror_checkbox.isChecked()

    def is_left_handed(self) -> bool:
        return self.left_handed_checkbox.isChecked()

    def get_click_threshold(self) -> int:
        return self.click_threshold.value()

    def get_drag_threshold(self) -> int:
        return self.drag_threshold.value()
