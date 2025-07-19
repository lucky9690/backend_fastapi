import cv2
import time
import os

CAPTURE_DIR = "captured_images"

def save_image(frame):
    if not os.path.exists(CAPTURE_DIR):
        os.makedirs(CAPTURE_DIR)
    filename = f"{CAPTURE_DIR}/capture_{int(time.time())}.jpg"
    cv2.imwrite(filename, frame)
    return filename
