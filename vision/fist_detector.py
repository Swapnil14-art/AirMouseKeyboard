from enum import Enum


class FistState(Enum):
    OPEN = "OPEN"
    HOLDING = "HOLDING"
    FIST_CONFIRMED = "FIST_CONFIRMED"


class FistDetector:
    """Detects fist gestures with timing confirmation and release debouncing."""

    def __init__(self, hold_duration_frames=10, exit_duration_frames=5):
        self.hold_duration_frames = hold_duration_frames
        self.exit_duration_frames = exit_duration_frames
        self.hold_counter = 0
        self.release_counter = 0
        self.state = FistState.OPEN

    def detect(self, fingers):
        """
        Detect fist gesture with timing confirmation and release debouncing.
        
        Args:
            fingers: List of 5 integers (0=finger closed, 1=finger open)
        
        Returns:
            FistState: Current state of the fist detection
        """
        is_fist = sum(fingers) == 0  # All fingers closed

        if self.state == FistState.FIST_CONFIRMED:
            if not is_fist:
                self.release_counter += 1
                if self.release_counter >= self.exit_duration_frames:
                    self.state = FistState.OPEN
                    self.hold_counter = 0
                    self.release_counter = 0
            else:
                self.release_counter = 0
        else:
            if is_fist:
                self.hold_counter += 1
                if self.hold_counter >= self.hold_duration_frames:
                    self.state = FistState.FIST_CONFIRMED
                    self.release_counter = 0
                else:
                    self.state = FistState.HOLDING
            else:
                self.hold_counter = 0
                self.state = FistState.OPEN

        return self.state

    def is_fist_confirmed(self):
        """Returns True if fist has been held for required duration."""
        return self.state == FistState.FIST_CONFIRMED

    def reset(self):
        """Reset the detector state."""
        self.hold_counter = 0
        self.release_counter = 0
        self.state = FistState.OPEN
