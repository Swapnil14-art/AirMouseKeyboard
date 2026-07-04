class FingerDetector:
    """Detects extended fingers from hand landmarks."""

    def get_fingers(self, landmarks):

        fingers = []

        # Thumb
        if landmarks[4][1] > landmarks[3][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Index
        fingers.append(
            1 if landmarks[8][2] < landmarks[6][2] else 0
        )

        # Middle
        fingers.append(
            1 if landmarks[12][2] < landmarks[10][2] else 0
        )

        # Ring
        fingers.append(
            1 if landmarks[16][2] < landmarks[14][2] else 0
        )

        # Pinky
        fingers.append(
            1 if landmarks[20][2] < landmarks[18][2] else 0
        )

        return fingers