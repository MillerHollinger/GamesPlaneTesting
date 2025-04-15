"""
Altered version of Josh's Testing_Video.py to work with a live camera.
"""

import cv2
import yaml
import time
from Games.DummyGame import *

YAML = "CameraCalibration\good_calibration.yaml"

print("Attempting to access camera.")
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

game = DummyGame(YAML)

print(f"Starting instance of {game.name}")
cv2.namedWindow("Live Capture", cv2.WINDOW_NORMAL)
times = []

while True:
    start_time = time.time()                # TIMER START
    ret, image = cap.read()
    if not ret: break

    pieces, anchors = game.process_image(image)
    for info in pieces + anchors:
        info.put_summary_graphic(image)
        info.put_bounds(image)
    # print(game.to_board(pieces))
    
    cv2.imshow("Live Capture", image)
    times.append(time.time() - start_time)  # TIMER END
    if cv2.waitKey(1) & 0xFF == ord('q'): # q to close
        break

cap.release()
cv2.destroyAllWindows()

avg_time = sum(times) / len(times)
print(f"Total time  : {sum(times):.3f} secs")
print(f"Total frames: {len(times)} frames")
print(f"Average time: {avg_time:.3f} s/frame")
print(f"Average FPS : {1/avg_time:.3f}")