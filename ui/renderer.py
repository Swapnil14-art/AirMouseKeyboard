"""
UI Renderer for AirControl.
Centralized rendering system for all UI elements.
"""

import cv2
import numpy as np
import time
from typing import Optional, Tuple, List
from ui.theme import theme
from ui.widgets import Panel, Card, Badge, Text, Button
from ui.animations import AnimationManager, PulseAnimation, RippleAnimation, FadeTransition
from gestures.gesture_types import Gesture
from managers.mode_manager import Mode


class UIRenderer:
    """Main UI renderer for AirControl application."""
    
    def __init__(self):
        self.animation_manager = AnimationManager()
        self.pulse_animation = PulseAnimation(duration=theme.animation.pulse_duration)
        self.ripple_animation = RippleAnimation(duration=theme.animation.ripple_duration)
        self.fade_transition = FadeTransition(duration=theme.animation.mode_transition_duration)
        
        self.last_mode = Mode.MOUSE
        self.fps_history: List[float] = []
        self.max_fps_history = 30
        
        # Cursor state
        self.cursor_position: Optional[Tuple[int, int]] = None
        self.is_pinching = False
        self.click_flash = 0.0
        
        # Hand trail
        self.hand_trail: List[Tuple[int, int]] = []
        
        # Notification system
        self.notifications: List[dict] = []
        
    def update(self) -> None:
        """Update animations and state."""
        self.animation_manager.update()
        self.pulse_animation.update()
        
        # Update FPS history
        current_time = time.time()
        
        # Update click flash
        if self.click_flash > 0:
            self.click_flash -= 0.1
            if self.click_flash < 0:
                self.click_flash = 0
        
        # Update notifications
        self._update_notifications()
    
    def draw_all(
        self,
        frame: np.ndarray,
        fps: float,
        mode: Mode,
        gesture: Gesture,
        has_pointer: bool,
        has_anchor: bool,
        pointer_pos: Optional[Tuple[int, int]] = None,
        fingers: Optional[List[int]] = None,
        is_dragging: bool = False,
        hovered_key: Optional[str] = None
    ) -> np.ndarray:
        """Draw all UI elements on the frame."""
        self.update()
        
        # Check for mode transition
        if mode != self.last_mode:
            self.fade_transition.start()
            self._add_notification(f"{mode.value} Mode", theme.colors.primary)
            self.last_mode = mode
        
        # Draw status panel
        self.draw_status_panel(frame, fps, mode, gesture, has_pointer, has_anchor)
        
        # Draw mode card
        self.draw_mode_card(frame, mode)
        
        # Draw gesture card
        self.draw_gesture_card(frame, gesture, is_dragging)
        
        # Draw tracking indicator
        self.draw_tracking_indicator(frame, has_pointer)
        
        # Draw FPS badge
        self.draw_fps_badge(frame, fps)
        
        # Draw custom cursor
        if pointer_pos is not None:
            self.cursor_position = pointer_pos
            self.draw_cursor(frame, pointer_pos, gesture == Gesture.LEFT_CLICK or is_dragging)
        
        # Draw notifications
        self.draw_notifications(frame)
        
        return frame
    
    def draw_status_panel(
        self,
        frame: np.ndarray,
        fps: float,
        mode: Mode,
        gesture: Gesture,
        has_pointer: bool,
        has_anchor: bool
    ) -> np.ndarray:
        """Draw the status panel with application information."""
        x = 10
        y = 10
        width = theme.spacing.status_panel_width
        height = theme.spacing.status_panel_height
        
        # Draw panel background
        Panel.draw(frame, x, y, width, height, theme.colors.background_opacity, theme.colors.border)
        
        # Draw title
        Text.draw_title(frame, "AirControl", x + theme.spacing.panel_padding_x, y + theme.spacing.panel_padding_y + 15)
        
        # Draw status items
        current_y = y + theme.spacing.panel_padding_y + 50
        line_height = 30
        
        # Tracking status
        tracking_icon = "✓" if has_pointer else "○"
        tracking_text = "Tracking" if has_pointer else "Searching"
        Text.draw_body(frame, f"{tracking_icon} {tracking_text}", x + theme.spacing.panel_padding_x, current_y)
        current_y += line_height
        
        # FPS
        Text.draw_body(frame, f"FPS {int(fps)}", x + theme.spacing.panel_padding_x, current_y)
        current_y += line_height
        
        # Mode
        Text.draw_body(frame, f"Mode {mode.value}", x + theme.spacing.panel_padding_x, current_y, color=theme.colors.primary)
        current_y += line_height
        
        # Gesture
        gesture_name = gesture.name if gesture != Gesture.NONE else "Idle"
        Text.draw_body(frame, f"Gesture {gesture_name}", x + theme.spacing.panel_padding_x, current_y)
        current_y += line_height
        
        # Pointer status
        pointer_status = "YES" if has_pointer else "NO"
        Text.draw_body(frame, f"Pointer {pointer_status}", x + theme.spacing.panel_padding_x, current_y)
        current_y += line_height
        
        # Anchor status
        anchor_status = "YES" if has_anchor else "NO"
        Text.draw_body(frame, f"Anchor {anchor_status}", x + theme.spacing.panel_padding_x, current_y)
        
        return frame
    
    def draw_mode_card(self, frame: np.ndarray, mode: Mode) -> np.ndarray:
        """Draw the current mode card with icon."""
        x = 10
        y = 340
        size = theme.spacing.mode_card_size
        
        # Get mode info
        if mode == Mode.MOUSE:
            icon = "🖱️"
            name = "Mouse"
            color = theme.colors.primary
        else:
            icon = "⌨️"
            name = "Keyboard"
            color = theme.colors.success
        
        # Apply fade transition
        opacity = self.fade_transition.update()
        
        # Draw card
        Panel.draw(frame, x, y, size, size, opacity * 0.6, color, 3)
        
        # Draw icon
        Text.draw_icon(frame, icon, x + size // 2 - 10, y + size // 2 + 10, size=30)
        
        # Draw name
        (text_w, text_h), _ = cv2.getTextSize(name, theme.fonts.font_face, theme.fonts.body_scale, theme.fonts.thickness_body)
        Text.draw_body(
            frame,
            name,
            x + (size - text_w) // 2,
            y + size - 10,
            color=color
        )
        
        return frame
    
    def draw_gesture_card(self, frame: np.ndarray, gesture: Gesture, is_dragging: bool) -> np.ndarray:
        """Draw the current gesture card."""
        x = 10
        y = 430
        width = theme.spacing.gesture_card_width
        height = theme.spacing.gesture_card_height
        
        # Get gesture info
        gesture_map = {
            Gesture.NONE: ("✊", "Fist", "Idle"),
            Gesture.LEFT_CLICK: ("👌", "Pinch", "Left Click"),
            Gesture.RIGHT_CLICK: ("✌️", "Victory", "Right Click"),
            Gesture.DRAG_START: ("✊", "Fist", "Drag Start"),
            Gesture.DRAGGING: ("✊", "Fist", "Dragging"),
            Gesture.DRAG_END: ("✊", "Fist", "Drag End")
        }
        
        icon, name, action = gesture_map.get(gesture, ("✊", "Unknown", "Idle"))
        
        if is_dragging:
            action = "Dragging"
        
        # Draw card
        Panel.draw(frame, x, y, width, height, 0.5, theme.colors.border)
        
        # Draw icon
        Text.draw_icon(frame, icon, x + theme.spacing.card_padding, y + theme.spacing.card_padding + 10, size=25)
        
        # Draw gesture name
        Text.draw_subtitle(frame, name, x + theme.spacing.card_padding + 40, y + theme.spacing.card_padding + 15)
        
        # Draw action
        Text.draw_body(frame, action, x + theme.spacing.card_padding + 40, y + theme.spacing.card_padding + 45)
        
        return frame
    
    def draw_tracking_indicator(self, frame: np.ndarray, has_pointer: bool) -> np.ndarray:
        """Draw the tracking status indicator."""
        x = 300
        y = 10
        size = 20
        
        # Determine color based on tracking status
        if has_pointer:
            color = theme.colors.success
        else:
            color = theme.colors.warning
        
        # Pulse animation
        pulse_scale = self.pulse_animation.update()
        pulse_size = int(size * pulse_scale)
        
        # Draw outer glow
        cv2.circle(frame, (x, y), pulse_size, color, 2)
        
        # Draw inner circle
        cv2.circle(frame, (x, y), size // 2, color, -1)
        
        return frame
    
    def draw_fps_badge(self, frame: np.ndarray, fps: float) -> np.ndarray:
        """Draw the FPS badge with color coding."""
        x = 10
        y = frame.shape[0] - 40
        
        # Determine color based on FPS
        if fps >= 28:
            color = theme.colors.success
        elif fps >= 20:
            color = theme.colors.warning
        else:
            color = theme.colors.danger
        
        # Draw badge
        Badge.draw(frame, x, y, f"FPS {int(fps)}", color)
        
        return frame
    
    def draw_cursor(self, frame: np.ndarray, position: Tuple[int, int], is_pinching: bool) -> np.ndarray:
        """Draw custom cursor with animations."""
        x, y = position
        size = theme.cursor.size
        
        # Update pinching state
        if is_pinching and not self.is_pinching:
            self.ripple_animation.start()
            self.click_flash = 1.0
        self.is_pinching = is_pinching
        
        # Get pulse scale
        pulse_scale = self.pulse_animation.update()
        
        # Draw glow
        glow_radius = int(theme.cursor.glow_intensity * pulse_scale)
        glow_overlay = frame.copy()
        cv2.circle(glow_overlay, (x, y), glow_radius, theme.colors.cursor_ring, -1)
        cv2.addWeighted(glow_overlay, 0.3, frame, 0.7, 0, frame)
        
        # Draw outer ring
        ring_radius = int(size * pulse_scale)
        cv2.circle(frame, (x, y), ring_radius, theme.colors.cursor_ring, theme.cursor.ring_thickness)
        
        # Draw inner circle
        cv2.circle(frame, (x, y), theme.cursor.inner_radius, theme.colors.cursor_inner, -1)
        
        # Draw crosshair
        crosshair_size = theme.cursor.crosshair_size
        cv2.line(frame, (x - crosshair_size, y), (x + crosshair_size, y), theme.colors.cursor_crosshair, 1)
        cv2.line(frame, (x, y - crosshair_size), (x, y + crosshair_size), theme.colors.cursor_crosshair, 1)
        
        # Draw ripple animation
        ripple_radius, ripple_opacity = self.ripple_animation.update()
        if ripple_radius > 0:
            ripple_overlay = frame.copy()
            cv2.circle(ripple_overlay, (x, y), int(ripple_radius), theme.colors.cursor_ring, 2)
            cv2.addWeighted(ripple_overlay, ripple_opacity, frame, 1 - ripple_opacity, 0, frame)
        
        # Draw click flash
        if self.click_flash > 0:
            flash_overlay = frame.copy()
            cv2.circle(flash_overlay, (x, y), size, theme.colors.success, -1)
            cv2.addWeighted(flash_overlay, self.click_flash * 0.5, frame, 1 - self.click_flash * 0.5, 0, frame)
        
        return frame
    
    def draw_hand(self, frame: np.ndarray, landmarks: List[Tuple[int, int, int]], label: str) -> np.ndarray:
        """Draw custom hand rendering."""
        # Update trail
        if len(landmarks) > 8:  # Index finger tip
            tip = landmarks[8]
            self.hand_trail.append((tip[1], tip[2]))
            if len(self.hand_trail) > theme.hand.trail_length:
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
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (5, 9), (9, 13), (13, 17)  # Palm
        ]
        
        for start_idx, end_idx in connections:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                start = landmarks[start_idx]
                end = landmarks[end_idx]
                cv2.line(frame, (start[1], start[2]), (end[1], end[2]), theme.colors.hand_bone, theme.hand.bone_thickness)
        
        # Draw joints
        for idx, lm in enumerate(landmarks):
            x, y = lm[1], lm[2]
            
            # Determine radius based on joint type
            if idx == 0:  # Wrist
                radius = theme.hand.wrist_radius
                color = hand_color
            elif idx in [4, 8, 12, 16, 20]:  # Fingertips
                radius = theme.hand.fingertip_radius
                color = theme.colors.hand_fingertip
            else:
                radius = theme.hand.joint_radius
                color = theme.colors.hand_joint
            
            # Draw glow for fingertips
            if idx in [4, 8, 12, 16, 20]:
                glow_overlay = frame.copy()
                cv2.circle(glow_overlay, (x, y), radius + 5, color, -1)
                cv2.addWeighted(glow_overlay, 0.3, frame, 0.7, 0, frame)
            
            cv2.circle(frame, (x, y), radius, color, -1)
        
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
        # Determine state
        if pressed:
            color = theme.colors.key_pressed
            opacity = 0.9
        elif hovered:
            color = theme.colors.key_hover
            opacity = 0.7
        else:
            color = theme.colors.key_normal
            opacity = 0.5
        
        # Draw key background
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
        
        # Draw key text
        font_scale = theme.fonts.body_scale
        thickness = theme.fonts.thickness_body
        (text_w, text_h), _ = cv2.getTextSize(
            key,
            theme.fonts.font_face,
            font_scale,
            thickness
        )
        
        # Scale down if text is too wide for the key
        while text_w > width - 10 and font_scale > 0.4:
            font_scale -= 0.1
            (text_w, text_h), _ = cv2.getTextSize(
                key,
                theme.fonts.font_face,
                font_scale,
                thickness
            )
        
        Text.draw(
            frame,
            key,
            x + (width - text_w) // 2,
            y + (height + text_h) // 2,
            scale=font_scale,
            color=theme.colors.text_primary,
            thickness=thickness
        )
        
        return frame
    
    def _add_notification(self, text: str, color: Tuple[int, int, int]) -> None:
        """Add a notification to the queue."""
        self.notifications.append({
            'text': text,
            'color': color,
            'start_time': time.time(),
            'duration': 2.0
        })
    
    def _update_notifications(self) -> None:
        """Update and remove expired notifications."""
        current_time = time.time()
        self.notifications = [
            notif for notif in self.notifications
            if current_time - notif['start_time'] < notif['duration']
        ]
    
    def draw_notifications(self, frame: np.ndarray) -> np.ndarray:
        """Draw active notifications."""
        frame_width = frame.shape[1]
        y = 60
        notification_height = 40
        spacing = 10
        
        for notif in self.notifications:
            # Calculate fade
            elapsed = time.time() - notif['start_time']
            duration = notif['duration']
            
            if elapsed < 0.2:  # Fade in
                opacity = elapsed / 0.2
            elif elapsed > duration - 0.2:  # Fade out
                opacity = (duration - elapsed) / 0.2
            else:
                opacity = 1.0
            
            # Calculate width
            (text_w, text_h), _ = cv2.getTextSize(
                notif['text'],
                theme.fonts.font_face,
                theme.fonts.body_scale,
                theme.fonts.thickness_body
            )
            width = text_w + 40
            
            # Center horizontally
            x = (frame_width - width) // 2
            
            # Draw notification
            overlay = frame.copy()
            radius = theme.radius.badge_radius
            cv2.rectangle(
                overlay,
                (x + radius, y),
                (x + width - radius, y + notification_height),
                notif['color'],
                -1
            )
            cv2.rectangle(
                overlay,
                (x, y + radius),
                (x + width, y + notification_height - radius),
                notif['color'],
                -1
            )
            cv2.circle(overlay, (x + radius, y + radius), radius, notif['color'], -1)
            cv2.circle(overlay, (x + width - radius, y + radius), radius, notif['color'], -1)
            cv2.circle(overlay, (x + radius, y + notification_height - radius), radius, notif['color'], -1)
            cv2.circle(overlay, (x + width - radius, y + notification_height - radius), radius, notif['color'], -1)
            
            cv2.addWeighted(overlay, opacity * 0.8, frame, 1 - opacity * 0.8, 0, frame)
            
            # Draw text
            Text.draw(
                frame,
                notif['text'],
                x + (width - text_w) // 2,
                y + notification_height - 12,
                scale=theme.fonts.body_scale,
                color=theme.colors.text_primary,
                thickness=theme.fonts.thickness_body
            )
            
            y += notification_height + spacing
        
        return frame
    
    def draw_active_area(self, frame: np.ndarray, margin_x: int, margin_y_top: int, margin_y_bottom: int) -> np.ndarray:
        """Draw the active tracking area rectangle."""
        h, w, _ = frame.shape
        
        # Draw rounded rectangle border
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (margin_x, margin_y_top),
            (w - margin_x, margin_y_bottom),
            theme.colors.primary,
            2
        )
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        return frame
