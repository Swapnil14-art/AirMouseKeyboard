import cv2
from ui.theme import theme


class KeyboardUI:
    """Dumb UI component that only draws the keyboard. No state management."""

    def __init__(self):
        self.keys = [
            ["Q","W","E","R","T","Y","U","I","O","P"],
            ["A","S","D","F","G","H","J","K","L"],
            ["Z","X","C","V","B","N","M","BACKSPACE"],
            ["SPACE"]
        ]
        self.key_width = 50
        self.key_height = 50
        self.start_x = 40
        self.start_y = 100
        self.hovered_key = None

    def get_key_width(self, key):
        """Get the width of the key (special handling for Space and Backspace)."""
        if key == "SPACE":
            return 300
        elif key == "BACKSPACE":
            return 120
        return self.key_width

    def get_hovered_key(self, x, y):
        """Get the key at the given coordinates."""
        current_y = self.start_y
        # Calculate max keyboard width based on Row 1 (10 keys of 50px with 8px spacing)
        max_keyboard_width = 10 * self.key_width + 9 * 8

        for row in self.keys:
            # Calculate total width of current row
            row_w = sum(self.get_key_width(k) for k in row) + (len(row) - 1) * 8
            # Center the row
            current_x = self.start_x + (max_keyboard_width - row_w) // 2

            for key in row:
                key_w = self.get_key_width(key)
                if (current_x <= x <= current_x + key_w and
                    current_y <= y <= current_y + self.key_height):
                    return key

                current_x += key_w + 8

            current_y += self.key_height + 8

        return None

    def draw(self, frame, visible=True, renderer=None):
        """Draw the keyboard on the frame if visible."""
        if not visible:
            return frame

        current_y = self.start_y
        # Calculate max keyboard width based on Row 1
        max_keyboard_width = 10 * self.key_width + 9 * theme.keyboard.key_spacing

        for row in self.keys:
            # Calculate total width of current row
            row_w = sum(self.get_key_width(k) for k in row) + (len(row) - 1) * theme.keyboard.key_spacing
            # Center the row
            current_x = self.start_x + (max_keyboard_width - row_w) // 2

            for key in row:
                hovered = (key == self.hovered_key)
                key_w = self.get_key_width(key)
                
                if renderer is not None:
                    # Use renderer for improved visual feedback
                    frame = renderer.draw_keyboard_key(
                        frame,
                        current_x,
                        current_y,
                        key_w,
                        self.key_height,
                        key,
                        hovered=hovered,
                        pressed=False
                    )
                else:
                    # Fallback to original drawing
                    color = theme.colors.key_normal
                    if hovered:
                        color = theme.colors.key_hover

                    cv2.rectangle(
                        frame,
                        (current_x, current_y),
                        (current_x + key_w, current_y + self.key_height),
                        color,
                        theme.keyboard.border_thickness
                    )

                    font_scale = 0.8
                    if len(key) > 1:
                        font_scale = 0.5
                    cv2.putText(
                        frame,
                        key,
                        (current_x + 10, current_y + 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale,
                        (255, 255, 255),
                        2
                    )

                current_x += key_w + theme.keyboard.key_spacing

            current_y += self.key_height + theme.keyboard.key_spacing

        return frame