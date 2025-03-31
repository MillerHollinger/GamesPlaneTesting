# New entry point to the system.
# Finds arucos on the board and converts them to board coordinates.

import cv2
from cv2 import aruco
import argparse
import imutils
import yaml
import numpy as np
from typing import List
from __future__ import annotations

from ArucoInfo import ArucoInfo

# 0. Load the calibration file.
print("[Step 0] Loading the calibration file.")
CAM_MATRIX = -1
DIST_COEFF = -1
with open("calibration.yaml") as stream:
    try:
        yaml_data = yaml.safe_load(stream)
        CAM_MATRIX = np.array(yaml_data['camera_matrix'])
        DIST_COEFF = np.array(yaml_data['dist_coeff'])
    except:
        print("Failed to load calibration.yaml")
        exit()

# 1. Load in a picture.
print("[Step 1] Loading the picture.")
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="Path to image with ARUCO tag(s).")
args = vars(ap.parse_args())
print(f"[Step 1] Chosen picture is {args["image"]}.")

# Rescale the image to a given value. Larger values run slower but higher accuracy likely.
IMAGE_SCALE = 600

image = cv2.imread(args["image"])
image = imutils.resize(image, width=IMAGE_SCALE)

# 2. Pull out the arucos.
print("[Step 2] Finding arucos in picture.")
dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
parameters = aruco.DetectorParameters()
(corners, ids, rejected) = aruco.detectMarkers(image, dictionary, parameters=parameters)

# 3. Make an arucoinfo object for each and store everything.
print("[Step 3] Building ArucoInfo objects.")
BLACK_PIECE_IDS = [1, 2, 3, 4, 5]
WHITE_PIECE_IDS = [6, 7, 8, 9, 10]
ANCHOR_MARKER_IDS = [11, 12, 13, 14, 15]
ANCHOR_MARKER_BOARD_POSITIONS = {
    11: (-1, 5), 
    12: (5, 5), 
    13: (-1, -1), 
    14: (5, -1), 
    15: (2, -2)
}
def type_for_id(id):
    if id in BLACK_PIECE_IDS:
        return "black"
    if id in WHITE_PIECE_IDS:
        return "white"
    if id in ANCHOR_MARKER_IDS:
        return "anchor"
    return "INVALID"

aruco_info = []
for (marker_corner, marker_id) in zip(corners, ids):
    arucoCorners = marker_corner.reshape((4, 2))
    (topLeft, topRight, bottomRight, bottomLeft) = arucoCorners
    
    # Convert coordinate pairs to ints.
    topRight = (int(topRight[0]), int(topRight[1]))
    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
    topLeft = (int(topLeft[0]), int(topLeft[1]))

    aruco_info.append(ArucoInfo((topRight, bottomRight, bottomLeft, topLeft), type_for_id(marker_id), marker_id))

# 4. Run to_world_coordinates on everything.
print("[Step 4] Calculating world coordinates for ArucoInfo objects.")
for info in aruco_info:
    info.to_world_coordinates()

# 5. For anchors, manually enter their board positions.
print("[Step 5] Setting anchor board positions.")
for info in aruco_info:
    if info.type == "anchor":
        info.set_board_position(ANCHOR_MARKER_BOARD_POSITIONS[info.id])

anchors = [info for info in aruco_info if info.type == "anchor"]

# 6. Extrapolate piece positions.
print("[Step 6] Extrapolating piece positions.")
for info in aruco_info:
    if info.type == "piece":
        info.to_board_position(anchors)


# 7. Show results.
print("[Step 7] Showing final results.")
print(f"{len(aruco_info)} ArUco markers were found.")
for info in aruco_info:
    print(info)
    