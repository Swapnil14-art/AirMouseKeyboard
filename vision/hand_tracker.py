import cv2
import mediapipe as mp

from vision.hand import Hand


class HandTracker:

    def __init__(self):

        self.mpHands = mp.solutions.hands

        self.hands = self.mpHands.Hands(

            static_image_mode=False,

            max_num_hands=2,

            min_detection_confidence=0.7,

            min_tracking_confidence=0.7

        )

        self.drawer = mp.solutions.drawing_utils

    def process(self, frame, mirror=True):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = self.hands.process(rgb)

        hands = []

        if result.multi_hand_landmarks:

            h, w, _ = frame.shape

            for hand_landmarks, handedness in zip(

                result.multi_hand_landmarks,
                result.multi_handedness

            ):

                label = handedness.classification[0].label
                if mirror:
                    label = "Right" if label == "Left" else "Left"

                landmarks = []

                for idx, lm in enumerate(hand_landmarks.landmark):

                    x = int(lm.x * w)
                    y = int(lm.y * h)

                    landmarks.append((idx, x, y))

                hands.append(

                    Hand(

                        label,

                        landmarks

                    )

                )

        return frame, hands