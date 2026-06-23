import cv2
import time
from typing import Tuple, Optional
import numpy as np
from .base import BaseSource

class VideoFileSource(BaseSource):
    def __init__(self, file_path: str, loop: bool = False, playback_speed: float = 1.0):
        self.file_path = file_path
        self.loop = loop
        self.playback_speed = playback_speed
        self.cap = None
        self._status = "offline"
        self._fps = 30
        self._last_frame_time = 0

    def start(self):
        self.cap = cv2.VideoCapture(self.file_path)
        if self.cap.isOpened():
            self._status = "playing"
            self._fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        else:
            self._status = "error"

    def stop(self):
        if self.cap:
            self.cap.release()
        self._status = "stopped"

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        if not self.cap or not self.cap.isOpened():
            return False, None
            
        # Basic pacing
        expected_delay = 1.0 / (self._fps * self.playback_speed)
        now = time.time()
        elapsed = now - self._last_frame_time
        if elapsed < expected_delay:
            time.sleep(expected_delay - elapsed)
            
        ret, frame = self.cap.read()
        self._last_frame_time = time.time()
        
        if not ret:
            if self.loop:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    self._status = "ended"
                    return False, None
            else:
                self._status = "ended"
                return False, None
                
        self._status = "playing"
        return True, frame

    def get_status(self) -> str:
        return self._status
