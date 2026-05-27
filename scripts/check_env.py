import sys
import numpy as np
import cv2

print("Python:", sys.version)
print("NumPy:", np.__version__)
print("OpenCV:", cv2.__version__)

try:
    from picamera2 import Picamera2
    print("Picamera2: OK")
except Exception as e:
    print("Picamera2: ERROR:", e)

print("Environment check complete.")
