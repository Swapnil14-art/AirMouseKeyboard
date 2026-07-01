import cv2
import mediapipe as mp


class HandTracker:

    def __init__(self):

        self.mpHands = mp.solutions.hands

        self.hands = self.mpHands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        self.drawer = mp.solutions.drawing_utils

    def process(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
        result = self.hands.process(rgb)
    
        landmarks = []
    
        if result.multi_hand_landmarks:
        
            hand = result.multi_hand_landmarks[0]
    
            self.drawer.draw_landmarks(
                frame,
                hand,
                self.mpHands.HAND_CONNECTIONS
            )
    
            h, w, _ = frame.shape
    
            for id, lm in enumerate(hand.landmark):
            
                x = int(lm.x * w)
                y = int(lm.y * h)
    
                landmarks.append((id, x, y))
    
        return frame, landmarks