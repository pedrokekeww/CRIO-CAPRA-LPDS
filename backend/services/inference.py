import requests
import base64
import cv2
import numpy as np
from config import settings

def infer_frame(frame: np.ndarray):
    """
    Sends a frame to Roboflow Inference API and returns predictions.
    """
    # Encode frame to base64
    _, buffer = cv2.imencode('.jpg', frame)
    img_str = base64.b64encode(buffer).decode("utf-8")
    
    # Roboflow hosted API format
    url = f"{settings.ROBOFLOW_API_URL}/{settings.ROBOFLOW_MODEL_ID}?api_key={settings.ROBOFLOW_API_KEY}"
    
    try:
        response = requests.post(
            url,
            data=img_str,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Inference error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Inference request failed: {e}")
        return None
