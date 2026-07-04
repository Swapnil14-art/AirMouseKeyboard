"""
Qt animation manager for AirControl desktop UI.
Provides non-blocking fade, slide, pulse, scale, and opacity animations.
"""

from typing import Optional

from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    Qt,
)
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget

from desktop.qt_theme import desktop_theme


class AnimationManager:
    """Factory for common widget animations."""

    @staticmethod
    def fade_in(widget: QWidget, duration: Optional[int] = None) -> QPropertyAnimation:
        """Fade a widget in using an opacity effect."""
        duration = duration or desktop_theme.animation.normal
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity", widget)
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        return animation

    @staticmethod
    def fade_out(widget: QWidget, duration: Optional[int] = None) -> QPropertyAnimation:
        """Fade a widget out using an opacity effect."""
        duration = duration or desktop_theme.animation.normal
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity", widget)
        animation.setDuration(duration)
        animation.setStartValue(effect.opacity())
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.InCubic)
        return animation

    @staticmethod
    def slide_in(widget: QWidget, start_offset: int = 24, duration: Optional[int] = None) -> QPropertyAnimation:
        """Slide a widget into place from below."""
        duration = duration or desktop_theme.animation.normal
        start_pos = widget.pos()
        end_pos = start_pos
        widget.move(start_pos.x(), start_pos.y() + start_offset)

        animation = QPropertyAnimation(widget, b"pos", widget)
        animation.setDuration(duration)
        animation.setStartValue(widget.pos())
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        return animation

    @staticmethod
    def pulse_opacity(widget: QWidget, duration: Optional[int] = None) -> QSequentialAnimationGroup:
        """Create a repeating pulse opacity animation."""
        duration = duration or desktop_theme.animation.pulse
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        half = duration // 2
        fade_down = QPropertyAnimation(effect, b"opacity", widget)
        fade_down.setDuration(half)
        fade_down.setStartValue(1.0)
        fade_down.setEndValue(0.45)
        fade_down.setEasingCurve(QEasingCurve.InOutSine)

        fade_up = QPropertyAnimation(effect, b"opacity", widget)
        fade_up.setDuration(half)
        fade_up.setStartValue(0.45)
        fade_up.setEndValue(1.0)
        fade_up.setEasingCurve(QEasingCurve.InOutSine)

        sequence = QSequentialAnimationGroup(widget)
        sequence.addAnimation(fade_down)
        sequence.addAnimation(fade_up)
        sequence.setLoopCount(-1)
        return sequence

    @staticmethod
    def scale_press(widget: QWidget, duration: Optional[int] = None) -> QSequentialAnimationGroup:
        """Quick press feedback using max width as a stand-in scale target."""
        duration = duration or desktop_theme.animation.fast
        original = widget.maximumWidth() if widget.maximumWidth() > 0 else widget.width()

        shrink = QPropertyAnimation(widget, b"maximumWidth", widget)
        shrink.setDuration(duration)
        shrink.setStartValue(original)
        shrink.setEndValue(max(original - 4, 1))
        shrink.setEasingCurve(QEasingCurve.OutCubic)

        expand = QPropertyAnimation(widget, b"maximumWidth", widget)
        expand.setDuration(duration)
        expand.setStartValue(max(original - 4, 1))
        expand.setEndValue(original)
        expand.setEasingCurve(QEasingCurve.OutBack)

        sequence = QSequentialAnimationGroup(widget)
        sequence.addAnimation(shrink)
        sequence.addAnimation(expand)
        return sequence

    @staticmethod
    def toast_enter(widget: QWidget) -> QParallelAnimationGroup:
        """Combined fade + slide entrance for toast notifications."""
        group = QParallelAnimationGroup(widget)
        group.addAnimation(AnimationManager.fade_in(widget, desktop_theme.animation.normal))
        group.addAnimation(AnimationManager.slide_in(widget, 18, desktop_theme.animation.normal))
        return group

    @staticmethod
    def toast_exit(widget: QWidget) -> QPropertyAnimation:
        """Fade a toast out before removal."""
        return AnimationManager.fade_out(widget, desktop_theme.animation.fast)
