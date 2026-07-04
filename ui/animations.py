"""
Animation system for AirControl UI.
Provides lightweight animation management for fade, scale, pulse, ripple, and slide effects.
"""

import time
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class AnimationType(Enum):
    """Types of animations supported."""
    FADE = "fade"
    SCALE = "scale"
    PULSE = "pulse"
    RIPPLE = "ripple"
    SLIDE = "slide"


@dataclass
class AnimationState:
    """State of a single animation."""
    animation_type: AnimationType
    start_time: float
    duration: float
    start_value: float
    end_value: float
    current_value: float
    is_complete: bool = False
    easing: str = "ease_out"  # ease_in, ease_out, ease_in_out, linear


class AnimationManager:
    """Manages UI animations with easing functions."""
    
    def __init__(self):
        self.animations: Dict[str, AnimationState] = {}
        self.last_frame_time = time.time()
    
    def start_animation(
        self,
        name: str,
        animation_type: AnimationType,
        duration: float,
        start_value: float = 0.0,
        end_value: float = 1.0,
        easing: str = "ease_out"
    ) -> None:
        """Start a new animation."""
        self.animations[name] = AnimationState(
            animation_type=animation_type,
            start_time=time.time(),
            duration=duration,
            start_value=start_value,
            end_value=end_value,
            current_value=start_value,
            easing=easing
        )
    
    def update(self) -> None:
        """Update all animations."""
        current_time = time.time()
        
        for name, anim in self.animations.items():
            elapsed = current_time - anim.start_time
            progress = min(elapsed / anim.duration, 1.0)
            
            # Apply easing
            eased_progress = self._apply_easing(progress, anim.easing)
            
            # Calculate current value
            anim.current_value = anim.start_value + (anim.end_value - anim.start_value) * eased_progress
            
            if progress >= 1.0:
                anim.is_complete = True
        
        # Remove completed animations
        self.animations = {
            name: anim for name, anim in self.animations.items()
            if not anim.is_complete
        }
    
    def get_value(self, name: str, default: float = 0.0) -> float:
        """Get current value of an animation."""
        if name in self.animations:
            return self.animations[name].current_value
        return default
    
    def is_animating(self, name: str) -> bool:
        """Check if an animation is currently running."""
        return name in self.animations
    
    def _apply_easing(self, progress: float, easing: str) -> float:
        """Apply easing function to progress."""
        if easing == "linear":
            return progress
        elif easing == "ease_in":
            return progress * progress
        elif easing == "ease_out":
            return 1 - (1 - progress) * (1 - progress)
        elif easing == "ease_in_out":
            return progress * progress * (3 - 2 * progress)
        return progress
    
    def clear(self) -> None:
        """Clear all animations."""
        self.animations.clear()


class PulseAnimation:
    """Specialized pulse animation for continuous pulsing effects."""
    
    def __init__(self, duration: float = 1.0, min_value: float = 0.8, max_value: float = 1.2):
        self.duration = duration
        self.min_value = min_value
        self.max_value = max_value
        self.start_time = time.time()
    
    def update(self) -> float:
        """Update and return current pulse value."""
        elapsed = time.time() - self.start_time
        progress = (elapsed % self.duration) / self.duration
        
        # Sine wave for smooth pulsing
        import math
        sine_value = math.sin(progress * 2 * math.pi)
        
        # Map sine from [-1, 1] to [min_value, max_value]
        normalized = (sine_value + 1) / 2  # [0, 1]
        return self.min_value + (self.max_value - self.min_value) * normalized
    
    def reset(self) -> None:
        """Reset the animation."""
        self.start_time = time.time()


class RippleAnimation:
    """Specialized ripple animation for click effects."""
    
    def __init__(self, duration: float = 0.5, max_radius: float = 50.0):
        self.duration = duration
        self.max_radius = max_radius
        self.start_time = None
        self.is_active = False
    
    def start(self) -> None:
        """Start the ripple animation."""
        self.start_time = time.time()
        self.is_active = True
    
    def update(self) -> tuple[float, float]:
        """Update and return (radius, opacity)."""
        if not self.is_active or self.start_time is None:
            return 0.0, 0.0
        
        elapsed = time.time() - self.start_time
        progress = min(elapsed / self.duration, 1.0)
        
        if progress >= 1.0:
            self.is_active = False
            return 0.0, 0.0
        
        radius = self.max_radius * progress
        opacity = 1.0 - progress  # Fade out as it expands
        
        return radius, opacity
    
    def reset(self) -> None:
        """Reset the animation."""
        self.start_time = None
        self.is_active = False


class FadeTransition:
    """Manages fade transitions for mode switching."""
    
    def __init__(self, duration: float = 0.3):
        self.duration = duration
        self.start_time = None
        self.is_active = False
        self.current_opacity = 1.0
    
    def start(self) -> None:
        """Start the fade transition."""
        self.start_time = time.time()
        self.is_active = True
    
    def update(self) -> float:
        """Update and return current opacity (0.0 to 1.0)."""
        if not self.is_active or self.start_time is None:
            return 1.0
        
        elapsed = time.time() - self.start_time
        progress = min(elapsed / self.duration, 1.0)
        
        if progress >= 1.0:
            self.is_active = False
            return 1.0
        
        # Fade out then in
        if progress < 0.5:
            # Fade out
            fade_progress = progress * 2
            self.current_opacity = 1.0 - fade_progress
        else:
            # Fade in
            fade_progress = (progress - 0.5) * 2
            self.current_opacity = fade_progress
        
        return self.current_opacity
