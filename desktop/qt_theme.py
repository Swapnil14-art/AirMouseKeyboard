"""
Qt desktop theme for AirControl.
Centralizes colors, typography, spacing, and animation timing for the desktop UI.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class QtColors:
    """Application color palette (hex strings for Qt stylesheets)."""

    background: str = "#0f1117"
    background_elevated: str = "#161b22"
    background_card: str = "#1c2333"
    background_card_hover: str = "#242d3f"

    primary: str = "#3b82f6"
    primary_glow: str = "#60a5fa"
    primary_dim: str = "#1e3a5f"

    success: str = "#22c55e"
    success_dim: str = "#14532d"
    warning: str = "#f59e0b"
    warning_dim: str = "#78350f"
    danger: str = "#ef4444"
    danger_dim: str = "#7f1d1d"

    text_primary: str = "#f8fafc"
    text_secondary: str = "#94a3b8"
    text_muted: str = "#64748b"

    border: str = "#2d3748"
    border_active: str = "#3b82f6"
    border_glow: str = "rgba(59, 130, 246, 0.45)"

    glass: str = "rgba(28, 35, 51, 0.82)"
    glass_border: str = "rgba(59, 130, 246, 0.25)"

    slider_groove: str = "#2d3748"
    slider_handle: str = "#3b82f6"

    camera_idle: str = "#3b82f6"
    camera_tracking: str = "#22c55e"
    camera_searching: str = "#f59e0b"
    camera_lost: str = "#ef4444"


@dataclass(frozen=True)
class QtFonts:
    """Typography configuration."""

    family: str = "Segoe UI"
    title_size: int = 22
    heading_size: int = 14
    body_size: int = 12
    small_size: int = 11
    card_value_size: int = 13


@dataclass(frozen=True)
class QtSpacing:
    """Layout spacing and sizing."""

    window_margin: int = 16
    panel_gap: int = 12
    card_gap: int = 8
    card_padding: int = 14
    card_radius: int = 14
    camera_radius: int = 16
    toast_height: int = 44
    toast_gap: int = 8
    header_height: int = 52


@dataclass(frozen=True)
class QtAnimation:
    """Animation duration constants in milliseconds."""

    fast: int = 150
    normal: int = 250
    slow: int = 400
    pulse: int = 1200
    toast_duration: int = 3200
    border_pulse: int = 1800


class DesktopTheme:
    """Aggregated desktop theme."""

    def __init__(self) -> None:
        self.colors = QtColors()
        self.fonts = QtFonts()
        self.spacing = QtSpacing()
        self.animation = QtAnimation()

    def global_stylesheet(self, variant: str = "neon") -> str:
        """Return the application-wide stylesheet."""
        if variant == "classic":
            colors = QtColors(
                background="#121212",
                background_elevated="#1e1e1e",
                background_card="#252525",
                background_card_hover="#2f2f2f",
                primary="#569cd6",
                primary_glow="#9cdcfe",
                primary_dim="#264f78",
                glass="rgba(37, 37, 37, 0.9)",
                glass_border="rgba(255, 255, 255, 0.08)",
            )
        else:
            colors = self.colors

        c = colors
        f = self.fonts
        return f"""
            QMainWindow {{
                background-color: {c.background};
            }}
            QWidget {{
                background-color: transparent;
                color: {c.text_primary};
                font-family: "{f.family}";
                font-size: {f.body_size}px;
            }}
            QSplitter::handle {{
                background-color: {c.border};
                width: 3px;
                border-radius: 1px;
            }}
            QSplitter::handle:hover {{
                background-color: {c.primary};
            }}
            QScrollBar:vertical {{
                background: {c.background_elevated};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {c.border};
                border-radius: 4px;
                min-height: 24px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {c.primary};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QStatusBar {{
                background-color: {c.background_elevated};
                color: {c.text_secondary};
                border-top: 1px solid {c.border};
                padding: 2px 8px;
            }}
            QToolTip {{
                background-color: {c.background_card};
                color: {c.text_primary};
                border: 1px solid {c.border_active};
                border-radius: 6px;
                padding: 6px;
            }}
        """


desktop_theme = DesktopTheme()
