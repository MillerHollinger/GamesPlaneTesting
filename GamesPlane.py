# New entry point to the system.
# Finds arucos on the board and converts them to board coordinates.


"""
ISSUE RIGHT NOW
- We need to:
1. Get a piece and an anchor.
2. Convert the piece's coordinates to being in the anchor's coordinate system.
- Translate it by -anchor_tvec.
- Rotate it by -anchor_rvec.

"""

from __future__ import annotations
import cv2
from cv2 import aruco
import argparse
import imutils
import yaml
import numpy as np
from typing import List
from ArucoInfo import ArucoInfo
import time

# 0. Load the calibration file.
print("[Step 0] Loading the calibration file.")
CAM_MATRIX = -1
DIST_COEFF = -1

# DEBUG NOTE: The generated calibration.yaml file is AWFUL and RUINS everything.
# This dummy file I put together, calib-dummy.yaml, works 1000% better, and actually returns the correct location for the marker.
# That said, note that it's not the real calibration file for any camera in particular, and should be replaced with a real calibration file.
with open("calib-dummy.yaml") as stream:
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
print("[Step 1] Chosen picture is " + args["image"])

# Rescale the image to a given value. Larger values run slower but higher accuracy likely.
IMAGE_SCALE = 800

start_time = time.time()

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
    aruco_info.append(ArucoInfo(marker_corner, type_for_id(marker_id[0]), marker_id[0]))

# 4. Run to_world_coordinates on everything.
print("[Step 4] Calculating world coordinates for ArucoInfo objects.")
for info in aruco_info:
    info.to_world_coordinates(CAM_MATRIX, DIST_COEFF)

# 5. For anchors, manually enter their board positions.
print("[Step 5] Setting anchor board positions.")
for info in aruco_info:
    if info.type == "anchor":
        info.set_board_position(ANCHOR_MARKER_BOARD_POSITIONS[info.id])

anchors = [info for info in aruco_info if info.type == "anchor"]

# 6. Extrapolate piece positions.
print("[Step 6] Extrapolating piece positions.")
for info in aruco_info:
    if info.type != "anchor":
        print(info.to_board_position(anchors))

# 7. Show results.
print("[Step 7] Showing final results.")
print(f"{len(aruco_info)} ArUco markers were found.")
test_image = image.copy()
for info in aruco_info:
    print(info)
    cv2.drawFrameAxes(image, CAM_MATRIX, DIST_COEFF, info.rvec, info.tvec, 2, 3)


#############################################
# DEBUG ZONE ################################
#############################################
    
def debug_tvec_add(info, diff):
    for i in range(len(info.tvec)):
        info.tvec[i] += diff[i]

tests = 10
DEBUG_MAPS = {
    119:    [0, -1, 0], # w -> sub Y
    115:    [0, 1, 0], # s -> add Y
    101:    [0, 0, 1], # e -> add Z
    113:    [0, 0, -1], # q -> sub Z
    100:    [1, 0, 0],  # d -> add X
    97:     [-1, 0, 0] # a -> sub X
}

chosen_piece = [x for x in aruco_info if x.type != "anchor"][0]
chosen_anchor = [x for x in aruco_info if x.type == "anchor"][0]
print(f"Chose {chosen_piece.id} <- {chosen_anchor.id}")
print(f"{(chosen_piece.tvec - chosen_anchor.tvec)} -> Distance of {np.linalg.norm(chosen_piece.tvec - chosen_anchor.tvec)}")

print(f"Execution took {(time.time() - start_time):.6f} seconds")

while True:
    tests -= 1
    my_image = test_image.copy()
    for info in aruco_info:
        cv2.drawFrameAxes(my_image, CAM_MATRIX, DIST_COEFF, (0, 0, 0), info.tvec, 2, 3)
        cv2.putText(my_image, str([round(e, 1) for e in info.tvec]), info.top_r, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.arrowedLine(my_image, chosen_anchor.center, chosen_piece.center, (255, 255, 255))
    cv2.imshow("Image", my_image)
    key = cv2.waitKey(0)

    for info in aruco_info:
        debug_tvec_add(info, DEBUG_MAPS[key])

    if key == 27:
        exit()