from typing import Tuple, Optional
import numpy as np

class BaseSource:
    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Returns (success, frame)"""
        return False, None

    def get_status(self) -> str:
        return "offline"
