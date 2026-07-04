import cv2

from config import CAMERA_ID


class Camera:
    """OpenCV camera capture wrapper."""

    def __init__(self, camera_id: int = CAMERA_ID):
        self.camera_id = camera_id
        self.mirror = True
        self.cap = cv2.VideoCapture(camera_id)
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

    def set_mirror(self, enabled: bool) -> None:
        """Enable or disable horizontal mirroring."""
        self.mirror = enabled

    def is_opened(self) -> bool:
        """Return True when the camera device is available."""
        return self.cap is not None and self.cap.isOpened()

    def get_frame(self):
        success, frame = self.cap.read()

        if not success:
            return None

        if self.mirror:
            frame = cv2.flip(frame, 1)

        return frame

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None