import cv2


class Camera:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def get_frame(self):
        success, frame = self.cap.read()

        if not success:
            return None

        frame = cv2.flip(frame, 1)

        return frame

    def release(self):
        self.cap.release()