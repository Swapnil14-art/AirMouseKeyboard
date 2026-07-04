class MouseSmoother:
    """Exponential smoothing for cursor movement."""

    def __init__(self, factor=5):
        self.factor = max(factor, 1)
        self.previous_x = 0
        self.previous_y = 0

    def set_factor(self, factor: int) -> None:
        """Update smoothing factor (higher = smoother)."""
        self.factor = max(int(factor), 1)

    def smooth(self, x, y):

        smooth_x = self.previous_x + (x - self.previous_x) / self.factor
        smooth_y = self.previous_y + (y - self.previous_y) / self.factor

        self.previous_x = smooth_x
        self.previous_y = smooth_y

        return smooth_x, smooth_y