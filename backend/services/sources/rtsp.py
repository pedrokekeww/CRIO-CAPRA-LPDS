import cv2
import time
from typing import Tuple, Optional
import numpy as np
from .base import BaseSource

class RTSPSource(BaseSource):
    def __init__(self, url: str):
        self.url = url
        self.cap = None
        self._status = "offline"

    def start(self):
        self.cap = cv2.VideoCapture(self.url)
        if self.cap.isOpened():
            self._status = "online"
        else:
            self._status = "error"

    def stop(self):
        if self.cap:
            self.cap.release()
        self._status = "offline"

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        if not self.cap or not self.cap.isOpened():
            self._status = "error"
            return False, None
        
        ret, frame = self.cap.read()
        if not ret:
            self._status = "error"
            # Attempt basic reconnect logic in the processor or here
            # For simplicity, we just return False and let manager reconnect
            return False, None
            
        self._status = "online"
        return True, frame

    def get_status(self) -> str:
        return self._status
