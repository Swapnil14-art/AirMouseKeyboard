from enum import Enum


class Mode(Enum):
    MOUSE = "MOUSE"
    KEYBOARD = "KEYBOARD"


class ModeManager:
    """Manages application mode switching between Mouse and Keyboard modes."""

    def __init__(self):
        self._mode = Mode.MOUSE

    def get_mode(self):
        """Get current mode."""
        return self._mode

    def set_mouse_mode(self):
        """Switch to Mouse Mode."""
        self._mode = Mode.MOUSE

    def set_keyboard_mode(self):
        """Switch to Keyboard Mode."""
        self._mode = Mode.KEYBOARD

    def is_mouse_mode(self):
        """Check if currently in Mouse Mode."""
        return self._mode == Mode.MOUSE

    def is_keyboard_mode(self):
        """Check if currently in Keyboard Mode."""
        return self._mode == Mode.KEYBOARD
