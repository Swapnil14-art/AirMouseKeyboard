from config import DOMINANT_HAND, ANCHOR_HAND


class HandManager:
    """Manages hand detection and assignment of pointer/anchor roles."""

    def __init__(self):
        self.dominant_hand = DOMINANT_HAND
        self.anchor_hand_label = ANCHOR_HAND
        self.pointer_hand = None
        self.anchor_hand = None
        self.hands = []

    def set_handedness(self, left_handed: bool) -> None:
        """Swap pointer/anchor hand labels for left-handed users."""
        if left_handed:
            self.dominant_hand = "Left"
            self.anchor_hand_label = "Right"
        else:
            self.dominant_hand = DOMINANT_HAND
            self.anchor_hand_label = ANCHOR_HAND

    def update(self, hands, mirror=True):
        """Update hand assignments based on detected hands."""
        self.hands = hands
        self.pointer_hand = None
        self.anchor_hand = None

        if len(hands) == 0:
            return

        if len(hands) == 1:
            # Single hand always controls the mouse
            self.pointer_hand = hands[0]
            return

        # If two hands are detected, assign labels based on relative X position of the wrist (landmark 0)
        # to guarantee one Left hand and one Right hand, correcting any MediaPipe label noise.
        hand1, hand2 = hands[0], hands[1]
        x1 = hand1.landmarks[0][1] if hand1.landmarks else 0
        x2 = hand2.landmarks[0][1] if hand2.landmarks else 0

        if mirror:
            # Smaller X is Right hand, larger X is Left hand
            if x1 < x2:
                hand1.label = "Right"
                hand2.label = "Left"
            else:
                hand1.label = "Left"
                hand2.label = "Right"
        else:
            # Smaller X is Left hand, larger X is Right hand
            if x1 < x2:
                hand1.label = "Left"
                hand2.label = "Right"
            else:
                hand1.label = "Right"
                hand2.label = "Left"

        for hand in hands:
            if hand.label == self.dominant_hand:
                self.pointer_hand = hand
            if hand.label == self.anchor_hand_label:
                self.anchor_hand = hand

    def has_pointer(self):
        """Check if pointer hand is detected."""
        return self.pointer_hand is not None

    def has_anchor(self):
        """Check if anchor hand is detected."""
        return self.anchor_hand is not None

    def has_two_hands(self):
        """Check if both pointer and anchor hands are detected."""
        return self.pointer_hand is not None and self.anchor_hand is not None