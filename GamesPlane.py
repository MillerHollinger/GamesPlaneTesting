# New entry point to the system.
# Finds arucos on the board and
# converts them to board coords.

import cv2
import yaml
import imutils
import argparse
import numpy as np
from cv2 import aruco
from ArucoInfo import ArucoInfo

# 0. Load the calibration file.
print("[Step 0] Loading the calibration file.")
CAM_MATRIX = -1
DIST_COEFF = -1
with open("calibration_josh.yaml") as stream:
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

# Rescale the image to a given value. Larger
# values run slower but give higher accuracy.
IMAGE_SCALE = 600
image = cv2.imread(args["image"])
image = imutils.resize(image, width=IMAGE_SCALE)
# Debug
# cv2.imshow(args["image"], image)
# cv2.waitKey(0)

# 2. Pull out the arucos.
print("[Step 2] Finding arucos in picture.")
dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
parameters = aruco.DetectorParameters()
(corners, ids, rejected) = aruco.detectMarkers(
    image, dictionary, parameters=parameters)
# Debug
if ids is not None:
    icopy = image.copy()
    aruco.drawDetectedMarkers(icopy, corners, ids)
    debug = f"{len(corners)} markers (IDs = {ids.flatten()}), {len(rejected)} rejected"
    print(debug)
    cv2.imshow(debug, icopy)
    cv2.waitKey(0)
else:
    print("Failed to find arucos in picture.")
    exit()

# 3. Build ArucoInfo objects.
print("[Step 3] Building ArucoInfo objects.")
BLACK_PIECE_IDS = [1, 2, 3, 4, 5]
WHITE_PIECE_IDS = [6, 7, 8, 9, 10]
ANCHOR_MARKER_IDS = [11, 12, 13, 14, 15]
BOARD_POSITIONS = {
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
for (corner, id) in zip(corners, ids):
    aruco_info.append(ArucoInfo(id[0], corner,
        type_for_id(id[0]), CAM_MATRIX, DIST_COEFF))

# 4. Calculate to_world_coordinates.
print("[Step 4] Calculating world coordinates.")
icopy = image.copy()
for info in aruco_info:
    icopy = info.to_world_coordinates(debug=icopy)
cv2.imshow(f"WORLD coords for {args["image"]}", icopy)
cv2.waitKey(0)

# 5. Calculate plot_board_coordinates.
print("[Step 5] Calculating board coordinates.")
info1, info2 = aruco_info
icopy = info1.plot_board_coordinates(info2, BOARD_POSITIONS, debug=icopy)
cv2.imshow(f"BOARD coordinates for {args["image"]}", icopy)
cv2.waitKey(0)
print("exit statement")
exit()

### old code ###

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

tests = 10
while tests > 0:
    tests -= 1
    my_image = test_image.copy()
    for info in aruco_info:
        cv2.drawFrameAxes(my_image, CAM_MATRIX, DIST_COEFF, info.rvec, info.tvec, 2, 3)
    cv2.imshow("Image", my_image)
    key = cv2.waitKey(0)
    print(key)