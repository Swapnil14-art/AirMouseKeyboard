"""
Simplified UI renderer for desktop application.
Only draws hand landmarks, cursor, and keyboard - no UI overlays.
"""

import cv2
import numpy as np
import time
from typing import Optional, Tuple, List
from ui.theme import theme


class SimpleRenderer:
    """Minimal renderer for camera feed only (no UI overlays)."""
    
    def __init__(self):
        self.hand_trail: List[Tuple[int, int]] = []
        self.cursor_position: Optional[Tuple[int, int]] = None
        self.is_pinching = False
        self.click_flash = 0.0
    
    def draw_hand(self, frame: np.ndarray, landmarks: List[Tuple[int, int, int]], label: str) -> np.ndarray:
        """Draw custom hand rendering with bones and joints."""
        # Update trail
        if len(landmarks) > 8:
            tip = landmarks[8]
            self.hand_trail.append((tip[1], tip[2]))
            if len(self.hand_trail) > 10:
                self.hand_trail.pop(0)
        
        # Determine hand color
        hand_color = theme.colors.hand_left if label == "Left" else theme.colors.hand_right
        
        # Draw trail
        for i, (tx, ty) in enumerate(self.hand_trail):
            alpha = i / len(self.hand_trail)
            trail_overlay = frame.copy()
            cv2.circle(trail_overlay, (tx, ty), 3, hand_color, -1)
            cv2.addWeighted(trail_overlay, alpha * 0.5, frame, 1 - alpha * 0.5, 0, frame)
        
        # Draw bones (connections)
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (0, 9), (9, 10), (10, 11), (11, 12),
            (0, 13), (13, 14), (14, 15), (15, 16),
            (0, 17), (17, 18), (18, 19), (19, 20),
            (5, 9), (9, 13), (13, 17)
        ]
        
        for start_idx, end_idx in connections:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                start = landmarks[start_idx]
                end = landmarks[end_idx]
                cv2.line(frame, (start[1], start[2]), (end[1], end[2]), theme.colors.hand_bone, 4)
        
        # Draw joints
        for idx, lm in enumerate(landmarks):
            x, y = lm[1], lm[2]
            
            if idx == 0:
                radius = 10
                color = hand_color
            elif idx in [4, 8, 12, 16, 20]:
                radius = 8
                color = theme.colors.hand_fingertip
            else:
                radius = 6
                color = theme.colors.hand_joint
            
            if idx in [4, 8, 12, 16, 20]:
                glow_overlay = frame.copy()
                cv2.circle(glow_overlay, (x, y), radius + 5, color, -1)
                cv2.addWeighted(glow_overlay, 0.3, frame, 0.7, 0, frame)
            
            cv2.circle(frame, (x, y), radius, color, -1)
        
        return frame
    
    def draw_cursor(self, frame: np.ndarray, position: Tuple[int, int], is_pinching: bool) -> np.ndarray:
        """Draw custom cursor on frame."""
        x, y = position
        size = 20
        
        if is_pinching and not self.is_pinching:
            self.click_flash = 1.0
        self.is_pinching = is_pinching
        
        if self.click_flash > 0:
            self.click_flash -= 0.1
            if self.click_flash < 0:
                self.click_flash = 0
        
        # Draw outer ring
        cv2.circle(frame, (x, y), size, theme.colors.cursor_ring, 3)
        
        # Draw inner circle
        cv2.circle(frame, (x, y), 6, theme.colors.cursor_inner, -1)
        
        # Draw crosshair
        cv2.line(frame, (x - 8, y), (x + 8, y), theme.colors.cursor_crosshair, 1)
        cv2.line(frame, (x, y - 8), (x, y + 8), theme.colors.cursor_crosshair, 1)
        
        # Draw click flash
        if self.click_flash > 0:
            flash_overlay = frame.copy()
            cv2.circle(flash_overlay, (x, y), size, theme.colors.success, -1)
            cv2.addWeighted(flash_overlay, self.click_flash * 0.5, frame, 1 - self.click_flash * 0.5, 0, frame)
        
        return frame
    
    def draw_keyboard_key(
        self,
        frame: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
        key: str,
        hovered: bool = False,
        pressed: bool = False
    ) -> np.ndarray:
        """Draw a keyboard key with visual feedback."""
        if pressed:
            color = theme.colors.key_pressed
            opacity = 0.9
        elif hovered:
            color = theme.colors.key_hover
            opacity = 0.7
        else:
            color = theme.colors.key_normal
            opacity = 0.5
        
        overlay = frame.copy()
        radius = 8
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
        
        font_scale = 0.8
        thickness = 2
        (text_w, text_h), _ = cv2.getTextSize(
            key,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            thickness
        )
        
        # Scale down if text is too wide for the key
        while text_w > width - 10 and font_scale > 0.4:
            font_scale -= 0.1
            (text_w, text_h), _ = cv2.getTextSize(
                key,
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                thickness
            )
        
        cv2.putText(
            frame,
            key,
            (x + (width - text_w) // 2, y + (height + text_h) // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),
            thickness
        )
        
        return frame
