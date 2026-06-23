import cv2
import queue
import time
from typing import Tuple, Optional
import numpy as np
from .base import BaseSource

class PassiveSource(BaseSource):
    """
    Used for Screen Share and Images, where frames are pushed to this source
    externally via API or WebSockets, rather than being pulled from a device.
    """
    def __init__(self, is_single_image: bool = False):
        self.frame_queue = queue.Queue(maxsize=10) # Keep memory low
        self._status = "offline"
        self.is_single_image = is_single_image

    def start(self):
        self._status = "waiting_for_frames"

    def stop(self):
        self._status = "offline"
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break

    def push_frame(self, frame: np.ndarray):
        if self._status == "offline":
            return
            
        if self.frame_queue.full():
            try:
                self.frame_queue.get_nowait() # drop oldest
            except queue.Empty:
                pass
                
        self.frame_queue.put(frame)
        self._status = "receiving"

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self._status == "offline":
            return False, None
            
        try:
            # Block for a short time to yield CPU
            frame = self.frame_queue.get(timeout=1.0)
            
            if self.is_single_image:
                # If it's a single static image, we don't want to loop rapidly processing it.
                # Just process it once and then block until a new one arrives.
                self._status = "processed"
                
            return True, frame
        except queue.Empty:
            if not self.is_single_image:
                self._status = "waiting_for_frames"
            return False, None

    def get_status(self) -> str:
        return self._status
