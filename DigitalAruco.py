# Stores information about an aruco marker seen through the camera.
# These objects are regenerated for each picture taken of the aruco.
# Miller Hollinger 2025

from __future__ import annotations
import cv2
from cv2 import aruco
import argparse
import imutils
import yaml
import numpy as np
from typing import List
from PhysicalAruco import * 
from PhysicalBoardInfo import *

class DigitalAruco:
    def __init__(self, raw_corners, phys: PhysicalAruco, cam_matrix, dist_coeff):
        if raw_corners.shape != (1, 4, 2):
            raise Exception(f"ArucoInfo object with invalid raw_corners: shape is {raw_corners.shape} (should be (4, 1, 2))")

        self.raw_corners = raw_corners

        # Reshape corners for easier use in UI.
        self.reshaped_corners = raw_corners.reshape((4, 2))
        (topLeft, topRight, bottomRight, bottomLeft) = self.reshaped_corners
        
        # Convert coordinate pairs to ints.
        self.top_r = (int(topRight[0]), int(topRight[1]))
        self.bot_r = (int(bottomRight[0]), int(bottomRight[1]))
        self.bot_l = (int(bottomLeft[0]), int(bottomLeft[1]))
        self.top_l = (int(topLeft[0]), int(topLeft[1]))
        self.center = (int(sum(x for x, y in self.reshaped_corners) / len(self.reshaped_corners)), int(sum(y for x, y in self.reshaped_corners) / len(self.reshaped_corners)))

        # World coordinates are not yet calculated.
        # rvec is Rodrigues' rotation vector form of the aruco's rotation.
        # tvec is the offset from the camera.
        self.rvec, self.tvec = None, None

        self.phys = phys

        # Anchored have precalculated board pos.
        if self.phys.anchored:   
            self.exact_board_position = self.phys.board_position
            self.closest_board_position = self.phys.board_position
        else:
            self.exact_board_position = None
            self.closest_board_position = None

        self.to_world_coordinates(cam_matrix, dist_coeff)


    # Converts my screen coordinates to world coordinates using camera calibration data.
    # Stores the world coordinates on the object.
    def to_world_coordinates(self, cam_matrix, dist_coeff):
        self.rvec, self.tvec, _ = aruco.estimatePoseSingleMarkers(self.raw_corners, self.phys.size, cam_matrix, dist_coeff)
        self.tvec = self.tvec[0][0]
        self.rvec = self.rvec[0][0]
        # print(f"Raw world coordinates of {self.id} are {self.tvec}")
    
    # Allows you to manually set where a marker is, for use on board positions only.
    def set_board_position(self, board_position):
        if not self.phys.anchored:
            raise Exception("Attempted to set an unanchored aruco's board position, which is not allowed. Use to_board_position to calculate the aruco's position relative to anchored markers.")
        self.exact_board_position = board_position
        self.closest_board_position = board_position

    # Return if rvec, tvec, and board_position set
    def fully_defined(self):
        return (not isinstance(self.rvec, list)) \
            or (not isinstance(self.tvec, list)) \
            or (self.exact_board_position == "not calculated") \
            or (self.closest_board_position == "not calculated")

    # Converts my world coordinates to a board position given some information about the board and the locations of the markers.
    # anchor_markers is one or more anchor arucos used as reference points.
    def to_board_position(self, anchor_markers: List[DigitalAruco], board: PhysicalBoardInfo):
        if self.phys.anchored:
            raise Exception("Tried to calculate the board position of an anchor, but anchors are precalculated.")
        
        if len(anchor_markers) < 1:
            raise Exception("You must provide at least 1 DigitalAruco object to calculate a board position.")

        # Verify that:
        # - Each anchor_marker is an "anchor"
        # - Each anchor_marker has its rvec, tvec, and board_position set
        for marker_data in anchor_markers:
            if not marker_data.phys.anchored:
                raise Exception("A marker in anchor_markers is not an anchor.")
            if not marker_data.fully_defined():
                raise Exception("A marker in anchor_markers is not fully defined (call to_world_coordinates and set_board_position on each anchor)")

        # We use each anchor to extract an approximate board position, then average and round at the end.
        pos_estimates = []

        for marker_data in anchor_markers:
            # Redefine the piece's pose in terms of the chosen anchor.
            _, rebased_tvec = DigitalAruco.change_basis(marker_data.rvec, marker_data.tvec, self.rvec, self.tvec)
            print(f"Locating Piece {self.phys.id}: Anchor {marker_data.phys.id} says an offset of {rebased_tvec}")
            
            # Use the tvec to get a board position.
            this_pos_estimate = [rebased_tvec[0] / board.cm_to_space, rebased_tvec[1] / board.cm_to_space]

            # Offset by the anchor's place.
            print(f"Locating Piece {self.phys.id}: Anchor {marker_data.phys.id} says raw estimate of {this_pos_estimate}")
            this_pos_estimate[0] += marker_data.closest_board_position[0]
            this_pos_estimate[1] += marker_data.closest_board_position[1]

            pos_estimates.append(this_pos_estimate)

            print(f"Locating Piece {self.phys.id}: Anchor {marker_data.phys.id} estimates at {round(this_pos_estimate[0], 2), round(this_pos_estimate[1], 2)}")

        # Save the exact (decimal) board pos in case we need it.
        self.exact_board_position = (sum(x for x, z in pos_estimates) / len(pos_estimates), sum(z for x, z in pos_estimates) / len(pos_estimates))

        # Ask the board for the closest space.
        self.closest_board_position = board.closest_valid_space(self.exact_board_position)

        return self.closest_board_position
    
    # Changes the basis of the second rvec, tvec to be in the first.
    def change_basis(rvec1, tvec1, rvec2, tvec2):
        # Convert to rotation matrices
        R1, _ = cv2.Rodrigues(rvec1)
        R2, _ = cv2.Rodrigues(rvec2)
        
        # Inverse of basis rotation (=transpose)
        R1_inv = np.transpose(R1)
        
        # Transform the rotation vector 
        R2_transformed = np.dot(R1_inv, R2) 
        
        # Transform and then rotate
        tvec2_transformed = np.dot(R1_inv, (tvec2 - tvec1)) 
        
        # Back to rodrigues form
        rvec2_transformed, _ = cv2.Rodrigues(R2_transformed) 

        return rvec2_transformed, tvec2_transformed
    
    def __str__(self):
        return f"{'Anchored' if self.phys.anchored else 'Unanchored'} ArUco ID {self.phys.id}, board position {self.closest_board_position}"

    # Adds summary info onto an image.
    def put_summary_graphic(self, image):
        image_center = np.array([image.shape[1] / 2, image.shape[0] / 2])
        # Find the closest point to the center.
        best_origin = [0, 0]
        closest = 9999
        for point in [self.top_l, self.top_r, self.bot_r, self.bot_l]:
            distance = np.linalg.norm(image_center - point)
            if distance < closest:
                best_origin = list(point)
                closest = distance

        color = (255, 255, 255) if self.phys.anchored else (128, 255, 255)

        # Add my position.
        cv2.putText(image, str(self.closest_board_position), best_origin, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Move down, add my tag and ID.
        best_origin[1] += 30
        cv2.putText(image, f"{self.phys.tag} {self.phys.id}", best_origin, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    def put_bounds(self, image):
        # Put the lines of my corners on the image.
        cornerOrder = [self.bot_l, self.top_l, self.top_r, self.bot_r, self.bot_l]
        color = (255, 255, 255) if self.phys.anchored else (128, 255, 255)
        for i in range(4):
            cv2.line(image, cornerOrder[i], cornerOrder[i+1], color, 1)

    def string_info(self):
        defined = "DEFINED" if self.fully_defined() else "PARTIAL"
        return f"{defined} ArucoInfo ID {self.phys.id} ({self.phys.tag}); center @ {self.center}; rvec {self.rvec}, tvec {self.tvec}; board position {self.closest_board_position} ({self.exact_board_position})"