# Find arucos and turn them into world coordinates.

import cv2
from cv2 import aruco
import argparse
import imutils
import yaml
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="Path to image with ARUCO tag(s).")
args = vars(ap.parse_args())


image = cv2.imread(args["image"])
image = imutils.resize(image, width=600)

dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
parameters = aruco.DetectorParameters()
(corners, ids, rejected) = aruco.detectMarkers(image, dictionary, parameters=parameters)
# print(corners)

aruco_data = []

# Render markers.
if len(corners) > 0:
    # Flatten ARUCO IDs list
    ids = ids.flatten()

    # Render each ARUCO bounding box
    for (markerCorner, markerID) in zip(corners, ids):

        # Read marker corners.
        arucoCorners = markerCorner.reshape((4, 2))
        (topLeft, topRight, bottomRight, bottomLeft) = arucoCorners
        
        # Convert coordinate pairs to ints.
        topRight = (int(topRight[0]), int(topRight[1]))
        bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
        bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
        topLeft = (int(topLeft[0]), int(topLeft[1]))
        
        # Corners are stored in this order:
        # 4 1
        # | |
        # 3-2

        aruco_data.append({
            'id': markerID,
            'corners_reshaped': arucoCorners,
            'corners_raw': markerCorner
        })

# aruco_data now contains all the information about arucos we found.
# [print(data) for data in aruco_data]
  
# Now, let's convert image data to world coordinates.
# Referenced https://stackoverflow.com/questions/68019526/how-can-i-get-the-distance-from-my-camera-to-an-opencv-aruco-marker
        
# TODO Move sizing info to some kind of config file.
marker_size_piece = 1.6 # In cm, marker size on pieces.
marker_size_anchor = 5.08 # In cm, marker size on board.

BLACK_PIECE_IDS = [1, 2, 3, 4, 5]
WHITE_PIECE_IDS = [6, 7, 8, 9, 10]
ANCHOR_MARKER_IDS = [11, 12, 13, 14, 15]
def type_for_id(id):
    if id in BLACK_PIECE_IDS:
        return "black"
    if id in WHITE_PIECE_IDS:
        return "white"
    if id in ANCHOR_MARKER_IDS:
        return "anchor"
    return "INVALID"

# Split markers into pieces and board anchors.
piece_data = []
anchor_data = []
#print(aruco_data)
for item in aruco_data:
    if type_for_id(item['id']) == "anchor":
        anchor_data.append(item)
    else:
        piece_data.append(item)

# https://stackoverflow.com/questions/1773805/how-can-i-parse-a-yaml-file-in-python
with open("calibration.yaml") as stream:
    try:
        yaml_data = yaml.safe_load(stream)
        cam_matrix = np.array(yaml_data['camera_matrix'])
        dist_coeff = np.array(yaml_data['dist_coeff'])
    except:
        print("Couldn't read yaml")
        exit()

# Show the axes
for data_type, marker_size in zip([piece_data, anchor_data], [marker_size_piece, marker_size_anchor]):
    if len(data_type) != 0:
        my_corners = [item['corners_raw'] for item in data_type]
        rvec, tvec, _ = aruco.estimatePoseSingleMarkers(my_corners, marker_size, cam_matrix, dist_coeff)
        #tvec[0][0][1] += 2

        # Draw the result.
        for i in range(len(rvec)):
            cv2.drawFrameAxes(image, cam_matrix, dist_coeff, rvec[i], tvec[i], 2, 3)
            cv2.putText(
                image, 
                type_for_id(data_type[i]['id']),
                (int(data_type[i]['corners_reshaped'][0][0]), int(data_type[i]['corners_reshaped'][0][1] - 15)), 
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, 
                (0, 255, 0), 
                2)


spaceWidth = 5.08

# One-on-one scaling test.
anchor_rvec, anchor_tvec, _ = aruco.estimatePoseSingleMarkers(anchor_data[0]['corners_raw'], marker_size_anchor, cam_matrix, dist_coeff)
piece_rvec, piece_tvec, _ = aruco.estimatePoseSingleMarkers(piece_data[0]['corners_raw'], marker_size_piece, cam_matrix, dist_coeff)
offset = (piece_tvec - anchor_tvec)[0][0]
print(f"The piece is offset from the anchor by {offset}")
#print("Piece", piece_tvec)
#print("Anchor", anchor_tvec)

# TODO Rotating a piece throws this off.
offsetX = round(offset[0] / spaceWidth) + 2
offsetY = round(offset[1] / spaceWidth) + 2
print(f"I think it's in space {offsetX} {offsetY} (bottom left is x 0, y 0)")

#cv2.drawFrameAxes(image, cam_matrix, dist_coeff, piece_rvec, np.array([[[-38.38122978, -48.26268281, 87.23867874]]]), 2, 3)
"""
# tvec[0][0][0] += 2 # Testing
# So basically -- the units are indeed centimeters. I can't figure out where the origin is -- it's supposed to be the camera -- but we can work around that
#  by redefining the coordinate system using the board arucos.

"""

cv2.imshow("Image", image)
cv2.waitKey(0)
