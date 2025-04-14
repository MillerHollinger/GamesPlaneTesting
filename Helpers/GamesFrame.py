# A GamesFrame handles interpreting the ArUco data for pictures.
# It allows you to extract deduced information about the image.
# To use it:
# 1. Instantiate the object with config information.
# 2. Feed it in an image using .process_image(image)
# 3. Check the returned DigitalAruco objects for information!
import yaml
import numpy as np
import cv2
from cv2 import aruco
from .PhysicalBoardInfo import *
from .DigitalAruco import *
import os

class GamesFrame:
    def __init__(self, camera_yaml: str, board_info: PhysicalBoardInfo):

        # Load the calibration file.
        print(os.getcwd())
        with open(camera_yaml) as stream:
            try:
                yaml_data = yaml.safe_load(stream)
                self.cam_matrix = np.array(yaml_data['camera_matrix'])
                self.dist_coeff = np.array(yaml_data['dist_coeff'])
            except:
                print(f"GamesPlaneConfig failed to read from {camera_yaml}")
                exit()
        
        # Record the board info.
        self.board_info = board_info

    # Given an image, returns DigitalAruco objects for every Aruco it could find.
    def process_image(self, image):
        # 1. Pull out the arucos.
        dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
        parameters = aruco.DetectorParameters()
        (corners, ids, rejected) = aruco.detectMarkers(image, dictionary, parameters=parameters)

        # 2. Make DigitalAruco objects for everything.
        anchors = []
        pieces = []
        for (marker_corner, marker_id) in zip(corners, ids):
            phys_aruco_info = self.board_info.aruco_info_for(marker_id)
            if phys_aruco_info == None:
                continue
            if phys_aruco_info.anchored:
                anchors.append(DigitalAruco(marker_corner, phys_aruco_info, self.cam_matrix, self.dist_coeff))
            else:
                pieces.append(DigitalAruco(marker_corner, phys_aruco_info, self.cam_matrix, self.dist_coeff))

        # 3. Define piece positions.
        for aru in pieces:
            print(aru)
            aru.to_board_position(anchors, self.board_info)

        return pieces, anchors