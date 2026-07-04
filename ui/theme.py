"""
Theme system for AirControl UI.
Provides centralized color palette, fonts, spacing, and UI configuration.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Colors:
    """Color palette for the UI."""
    
    # Background
    background: Tuple[int, int, int] = (0, 0, 0)
    background_opacity: float = 0.5
    
    # Primary
    primary: Tuple[int, int, int] = (59, 130, 246)
    
    # Status colors
    success: Tuple[int, int, int] = (34, 197, 94)
    warning: Tuple[int, int, int] = (245, 158, 11)
    danger: Tuple[int, int, int] = (239, 68, 68)
    
    # Text
    text_primary: Tuple[int, int, int] = (255, 255, 255)
    text_secondary: Tuple[int, int, int] = (200, 200, 200)
    
    # Borders
    border: Tuple[int, int, int] = (100, 100, 100)
    
    # Hand rendering
    hand_bone: Tuple[int, int, int] = (220, 220, 220)
    hand_joint: Tuple[int, int, int] = (59, 130, 246)
    hand_fingertip: Tuple[int, int, int] = (96, 165, 250)
    hand_left: Tuple[int, int, int] = (59, 130, 246)
    hand_right: Tuple[int, int, int] = (239, 68, 68)
    
    # Cursor
    cursor_ring: Tuple[int, int, int] = (59, 130, 246)
    cursor_inner: Tuple[int, int, int] = (255, 255, 255)
    cursor_crosshair: Tuple[int, int, int] = (255, 255, 255)
    
    # Keyboard
    key_normal: Tuple[int, int, int] = (100, 100, 100)
    key_hover: Tuple[int, int, int] = (59, 130, 246)
    key_pressed: Tuple[int, int, int] = (34, 197, 94)


@dataclass
class Fonts:
    """Font configuration using OpenCV fonts."""
    
    title_scale: float = 1.2
    subtitle_scale: float = 1.0
    body_scale: float = 0.8
    small_scale: float = 0.6
    
    thickness_title: int = 3
    thickness_subtitle: int = 2
    thickness_body: int = 2
    thickness_small: int = 1
    
    font_face = 0  # cv2.FONT_HERSHEY_SIMPLEX


@dataclass
class Spacing:
    """Spacing and sizing configuration."""
    
    # Panel padding
    panel_padding_x: int = 20
    panel_padding_y: int = 15
    
    # Card spacing
    card_margin: int = 10
    card_padding: int = 15
    
    # Element spacing
    element_spacing: int = 10
    line_spacing: int = 8
    
    # Status panel
    status_panel_width: int = 280
    status_panel_height: int = 320
    
    # Mode card
    mode_card_size: int = 80
    
    # Gesture card
    gesture_card_width: int = 200
    gesture_card_height: int = 100
    
    # FPS badge
    fps_badge_width: int = 80
    fps_badge_height: int = 30


@dataclass
class Radius:
    """Corner radius configuration."""
    
    panel_radius: int = 15
    card_radius: int = 12
    button_radius: int = 8
    badge_radius: int = 6


@dataclass
class Animation:
    """Animation timing configuration."""
    
    fade_duration: float = 0.3  # seconds
    pulse_duration: float = 1.0
    ripple_duration: float = 0.5
    slide_duration: float = 0.3
    mode_transition_duration: float = 0.3
    
    # Frame-based timing (assuming 30 FPS)
    fade_frames: int = 9
    pulse_frames: int = 30
    ripple_frames: int = 15
    slide_frames: int = 9
    mode_transition_frames: int = 9


@dataclass
class Cursor:
    """Cursor rendering configuration."""
    
    size: int = 20
    ring_thickness: int = 3
    inner_radius: int = 6
    crosshair_size: int = 8
    glow_intensity: int = 30
    pulse_amplitude: int = 5


@dataclass
class Hand:
    """Hand rendering configuration."""
    
    bone_thickness: int = 4
    joint_radius: int = 6
    fingertip_radius: int = 8
    wrist_radius: int = 10
    glow_radius: int = 15
    trail_length: int = 10


@dataclass
class Keyboard:
    """Keyboard UI configuration."""
    
    key_width: int = 40
    key_height: int = 40
    key_spacing: int = 8
    start_x: int = 170
    start_y: int = 10
    border_thickness: int = 2
    pressed_animation_frames: int = 5


class Theme:
    """Main theme class aggregating all UI configuration."""
    
    def __init__(self):
        self.colors = Colors()
        self.fonts = Fonts()
        self.spacing = Spacing()
        self.radius = Radius()
        self.animation = Animation()
        self.cursor = Cursor()
        self.hand = Hand()
        self.keyboard = Keyboard()
    
    def get_color_with_opacity(self, color: Tuple[int, int, int], opacity: float) -> Tuple[int, int, int, int]:
        """Add opacity to a color (returns RGBA)."""
        return (*color, int(opacity * 255))


# Global theme instance
theme = Theme()
