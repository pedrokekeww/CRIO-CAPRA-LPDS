import requests
import base64
import numpy as np
import cv2

url = "https://detect.roboflow.com/ppe-vum8g/2?api_key=5QaqrsR4nedevUxjLzbq"

# Create a dummy image
img = np.zeros((480, 640, 3), dtype=np.uint8)
cv2.putText(img, "Test", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
_, buffer = cv2.imencode('.jpg', img)
img_str = base64.b64encode(buffer).decode("utf-8")

response = requests.post(url, data=img_str, headers={"Content-Type": "application/x-www-form-urlencoded"})
print("Status Code:", response.status_code)
print("Response:", response.text)
