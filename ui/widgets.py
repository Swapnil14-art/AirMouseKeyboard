"""
UI widgets for AirControl.
Provides reusable UI components like panels, cards, badges, and buttons.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List
from ui.theme import theme


class Panel:
    """Glassmorphism panel with rounded corners."""
    
    @staticmethod
    def draw(
        frame: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
        opacity: float = 0.5,
        border_color: Optional[Tuple[int, int, int]] = None,
        border_thickness: int = 2
    ) -> np.ndarray:
        """Draw a glassmorphism panel."""
        overlay = frame.copy()
        
        # Draw rounded rectangle
        radius = theme.radius.panel_radius
        cv2.rectangle(
            overlay,
            (x + radius, y),
            (x + width - radius, y + height),
            theme.colors.background,
            -1
        )
        cv2.rectangle(
            overlay,
            (x, y + radius),
            (x + width, y + height - radius),
            theme.colors.background,
            -1
        )
        
        # Draw corners
        cv2.circle(overlay, (x + radius, y + radius), radius, theme.colors.background, -1)
        cv2.circle(overlay, (x + width - radius, y + radius), radius, theme.colors.background, -1)
        cv2.circle(overlay, (x + radius, y + height - radius), radius, theme.colors.background, -1)
        cv2.circle(overlay, (x + width - radius, y + height - radius), radius, theme.colors.background, -1)
        
        # Apply opacity
        cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)
        
        # Draw border
        if border_color is not None:
            Panel._draw_rounded_border(
                frame,
                x, y, width, height,
                radius,
                border_color,
                border_thickness
            )
        
        return frame
    
    @staticmethod
    def _draw_rounded_border(
        frame: np.ndarray,
        x: int, y: int, width: int, height: int,
        radius: int,
        color: Tuple[int, int, int],
        thickness: int
    ) -> None:
        """Draw rounded rectangle border."""
        # Top line
        cv2.line(frame, (x + radius, y), (x + width - radius, y), color, thickness)
        # Bottom line
        cv2.line(frame, (x + radius, y + height), (x + width - radius, y + height), color, thickness)
        # Left line
        cv2.line(frame, (x, y + radius), (x, y + height - radius), color, thickness)
        # Right line
        cv2.line(frame, (x + width, y + radius), (x + width, y + height - radius), color, thickness)
        
        # Corner arcs
        cv2.ellipse(frame, (x + radius, y + radius), (radius, radius), 180, 0, 90, color, thickness)
        cv2.ellipse(frame, (x + width - radius, y + radius), (radius, radius), 270, 0, 90, color, thickness)
        cv2.ellipse(frame, (x + radius, y + height - radius), (radius, radius), 90, 0, 90, color, thickness)
        cv2.ellipse(frame, (x + width - radius, y + height - radius), (radius, radius), 0, 0, 90, color, thickness)


class Card:
    """Card widget for displaying information."""
    
    @staticmethod
    def draw(
        frame: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str,
        value: str,
        icon: str = "",
        opacity: float = 0.6,
        border_color: Optional[Tuple[int, int, int]] = None
    ) -> np.ndarray:
        """Draw a card with title and value."""
        # Draw panel
        Panel.draw(frame, x, y, width, height, opacity, border_color)
        
        # Draw icon if provided
        if icon:
            Text.draw_icon(frame, icon, x + theme.spacing.card_padding, y + theme.spacing.card_padding + 10)
        
        # Draw title
        Text.draw(
            frame,
            title,
            x + theme.spacing.card_padding + (30 if icon else 0),
            y + theme.spacing.card_padding + 10,
            scale=theme.fonts.small_scale,
            color=theme.colors.text_secondary,
            thickness=theme.fonts.thickness_small
        )
        
        # Draw value
        Text.draw(
            frame,
            value,
            x + theme.spacing.card_padding + (30 if icon else 0),
            y + theme.spacing.card_padding + 35,
            scale=theme.fonts.subtitle_scale,
            color=theme.colors.text_primary,
            thickness=theme.fonts.thickness_subtitle
        )
        
        return frame


class Badge:
    """Small badge for status indicators."""
    
    @staticmethod
    def draw(
        frame: np.ndarray,
        x: int,
        y: int,
        text: str,
        color: Tuple[int, int, int],
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> np.ndarray:
        """Draw a status badge."""
        if width is None:
            width = theme.spacing.fps_badge_width
        if height is None:
            height = theme.spacing.fps_badge_height
        
        # Calculate text size
        (text_w, text_h), _ = cv2.getTextSize(
            text,
            theme.fonts.font_face,
            theme.fonts.small_scale,
            theme.fonts.thickness_small
        )
        
        # Adjust width to fit text
        badge_width = max(width, text_w + 20)
        
        # Draw rounded background
        radius = theme.radius.badge_radius
        cv2.rectangle(
            frame,
            (x + radius, y),
            (x + badge_width - radius, y + height),
            color,
            -1
        )
        cv2.rectangle(
            frame,
            (x, y + radius),
            (x + badge_width, y + height - radius),
            color,
            -1
        )
        cv2.circle(frame, (x + radius, y + radius), radius, color, -1)
        cv2.circle(frame, (x + badge_width - radius, y + radius), radius, color, -1)
        cv2.circle(frame, (x + radius, y + height - radius), radius, color, -1)
        cv2.circle(frame, (x + badge_width - radius, y + height - radius), radius, color, -1)
        
        # Draw text
        Text.draw(
            frame,
            text,
            x + (badge_width - text_w) // 2,
            y + height - 8,
            scale=theme.fonts.small_scale,
            color=theme.colors.text_primary,
            thickness=theme.fonts.thickness_small
        )
        
        return frame


class Text:
    """Text rendering utilities."""
    
    @staticmethod
    def draw(
        frame: np.ndarray,
        text: str,
        x: int,
        y: int,
        scale: float = 1.0,
        color: Tuple[int, int, int] = (255, 255, 255),
        thickness: int = 2,
        font_face: int = 0
    ) -> np.ndarray:
        """Draw text with specified parameters."""
        cv2.putText(
            frame,
            text,
            (x, y),
            font_face,
            scale,
            color,
            thickness
        )
        return frame
    
    @staticmethod
    def draw_title(frame: np.ndarray, text: str, x: int, y: int) -> np.ndarray:
        """Draw title text."""
        return Text.draw(
            frame,
            text,
            x, y,
            scale=theme.fonts.title_scale,
            color=theme.colors.text_primary,
            thickness=theme.fonts.thickness_title
        )
    
    @staticmethod
    def draw_subtitle(frame: np.ndarray, text: str, x: int, y: int) -> np.ndarray:
        """Draw subtitle text."""
        return Text.draw(
            frame,
            text,
            x, y,
            scale=theme.fonts.subtitle_scale,
            color=theme.colors.text_primary,
            thickness=theme.fonts.thickness_subtitle
        )
    
    @staticmethod
    def draw_body(frame: np.ndarray, text: str, x: int, y: int, color: Tuple[int, int, int] = None) -> np.ndarray:
        """Draw body text."""
        if color is None:
            color = theme.colors.text_secondary
        return Text.draw(
            frame,
            text,
            x, y,
            scale=theme.fonts.body_scale,
            color=color,
            thickness=theme.fonts.thickness_body
        )
    
    @staticmethod
    def draw_small(frame: np.ndarray, text: str, x: int, y: int) -> np.ndarray:
        """Draw small label text."""
        return Text.draw(
            frame,
            text,
            x, y,
            scale=theme.fonts.small_scale,
            color=theme.colors.text_secondary,
            thickness=theme.fonts.thickness_small
        )
    
    @staticmethod
    def draw_icon(frame: np.ndarray, icon: str, x: int, y: int, size: int = 20) -> np.ndarray:
        """Draw an emoji icon."""
        return Text.draw(
            frame,
            icon,
            x, y,
            scale=0.8,
            color=theme.colors.text_primary,
            thickness=2
        )


class ProgressBar:
    """Progress bar widget."""
    
    @staticmethod
    def draw(
        frame: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
        progress: float,  # 0.0 to 1.0
        color: Tuple[int, int, int] = (59, 130, 246),
        background_color: Tuple[int, int, int] = (100, 100, 100)
    ) -> np.ndarray:
        """Draw a progress bar."""
        # Draw background
        cv2.rectangle(frame, (x, y), (x + width, y + height), background_color, -1)
        
        # Draw progress
        progress_width = int(width * progress)
        cv2.rectangle(frame, (x, y), (x + progress_width, y + height), color, -1)
        
        return frame


class Button:
    """Interactive button widget."""
    
    @staticmethod
    def draw(
        frame: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        hovered: bool = False,
        pressed: bool = False
    ) -> np.ndarray:
        """Draw a button with hover/press states."""
        # Determine color based on state
        if pressed:
            color = theme.colors.key_pressed
            opacity = 0.8
        elif hovered:
            color = theme.colors.key_hover
            opacity = 0.7
        else:
            color = theme.colors.key_normal
            opacity = 0.5
        
        # Draw button background
        overlay = frame.copy()
        radius = theme.radius.button_radius
        cv2.rectangle(
            overlay,
            (x + radius, y),
            (x + width - radius, y + height),
            color,
            -1
        )
        cv2.rectangle(
            overlay,
            (x, y + radius),
            (x + width, y + height - radius),
            color,
            -1
        )
        cv2.circle(overlay, (x + radius, y + radius), radius, color, -1)
        cv2.circle(overlay, (x + width - radius, y + radius), radius, color, -1)
        cv2.circle(overlay, (x + radius, y + height - radius), radius, color, -1)
        cv2.circle(overlay, (x + width - radius, y + height - radius), radius, color, -1)
        
        cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)
        
        # Draw text
        (text_w, text_h), _ = cv2.getTextSize(
            text,
            theme.fonts.font_face,
            theme.fonts.body_scale,
            theme.fonts.thickness_body
        )
        
        Text.draw(
            frame,
            text,
            x + (width - text_w) // 2,
            y + (height + text_h) // 2,
            scale=theme.fonts.body_scale,
            color=theme.colors.text_primary,
            thickness=theme.fonts.thickness_body
        )
        
        return frame
