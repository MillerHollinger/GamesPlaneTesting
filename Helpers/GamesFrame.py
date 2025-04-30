# A GamesFrame handles interpreting the ArUco data for pictures.
# It allows you to extract deduced information about the image.
# To use it:
# 1. Instantiate the object with config information.
# 2. Feed it in an image using .process_image(image)
# 3. Check the returned DigitalAruco objects for information!
import yaml
import numpy as np
from cv2 import aruco
from .PhysicalBoardInfo import *
from .DigitalAruco import *
    
class GamesFrame:
    def __init__(self, camera_yaml: str, board_info: PhysicalBoardInfo):

        # Load the calibration file.
        if ".yaml" in camera_yaml:
            camera_yaml = open(camera_yaml)
        try:
            yaml_data = yaml.safe_load(camera_yaml)
            self.cam_matrix = np.array(yaml_data['camera_matrix'])
            self.dist_coeff = np.array(yaml_data['dist_coeff'])
        except:
            print(f"GamesPlaneConfig failed to read from {camera_yaml}")
            exit()
        
        # Record the board info.
        self.board_info = board_info

    # Given an image, returns DigitalAruco objects for every Aruco it could find.
    def process_image(self, image, give_reasoning: bool = False):
        # 1. Pull out the arucos.
        dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
        parameters = aruco.DetectorParameters()
        (corners, ids, rejected) = aruco.detectMarkers(image, dictionary, parameters=parameters)

        # 2. Make DigitalAruco objects for everything.
        anchors = []
        pieces = []
        reasoning = []

        if len(corners) == 0:
            return pieces, anchors, reasoning

        for (marker_corner, marker_id) in zip(corners, ids):
            phys_aruco_info = self.board_info.aruco_info_for(marker_id)
            if phys_aruco_info == None:
                continue
            if phys_aruco_info.anchored:
                anchors.append(DigitalAruco(marker_corner, phys_aruco_info, self.cam_matrix, self.dist_coeff))
            else:
                pieces.append(DigitalAruco(marker_corner, phys_aruco_info, self.cam_matrix, self.dist_coeff))

        # 3. Define piece positions.
        if len(anchors) > 0:
            for aru in pieces:
                #print(aru)
                _, reason = aru.to_board_position(anchors, self.board_info, give_reasoning)
                reasoning.append(reason)

        if not give_reasoning:
            return pieces, anchors, None
        else:
            return pieces, anchors, reasoning