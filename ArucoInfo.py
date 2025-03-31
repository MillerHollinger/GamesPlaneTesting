# The ArucoInfo class stores data about an Aruco marker.
# Miller Hollinger 2025

import cv2
from cv2 import aruco
import argparse
import imutils
import yaml
import numpy as np
from typing import List
from __future__ import annotations

class ArucoInfo:
    # corners: the aruco's four corners, stored in this order:
        # 4 1
        # | |
        # 3-2
    # marker_type: "anchor", "white", "black"
        # Represents what the marker's position represents.
    VALID_MARKER_TYPES = ["anchor", "white", "black"]
    def __init__(self, corners, marker_type, id):
        if len(corners) != 4:
            raise Exception(f"ArucoInfo object with an invalid number of corners: {len(corners)} (should be 4)")
        if len(corners[0]) != 2:
            raise Exception(f"ArucoInfo object with an invalid number of coordinates in a corner: {len(corners[0])} (should be 2)")
        if not (marker_type in self.VALID_MARKER_TYPES):
            raise Exception(f"ArucoInfo object with an invalid marker_type: {marker_type} (should be {self.VALID_MARKER_TYPES})")
        
        self.corners = corners
        self.id = id

        # Shorthand access to corners and center.
        self.top_r = corners[0]
        self.bot_r = corners[1]
        self.bot_l = corners[2]
        self.top_l = corners[3]
        self.center = (sum(x for x, y in corners) / len(corners), sum(y for x, y in corners) / len(corners))

        # Corners reshaped so they're structured like the actual object.
        self.corners_reshaped = ((self.top_l, self.top_r), (self.bot_l, self.bot_r))

        # Save my type.
        self.type = marker_type

        # World coordinates are not yet calculated.
        # rvec is Rodrigues' rotation vector form of the aruco's rotation.
        # tvec is the offset from the camera.
        self.rvec, self.tvec = "not calculated", "not calculated"

        # Board position is not yet calculated
        self.exact_board_position = "not calculated"
        self.closest_board_position = "not calculated"

    # In cm, how wide a (square) space on the board is.
    SPACE_WIDTH = 5.05

    # In cm, maps how large a marker should be to a side.
    TYPE_TO_SIZE = {
        "anchor": 5.05,
        "black": 1.66,
        "white": 1.66
    }
    def marker_size(self):
        return self.TYPE_TO_SIZE[self.type]

    # Converts my aruco coordinates to world coordinates using the camera calibration file.
    # Stores the world coordinates on the object.
    def to_world_coordinates(self, cam_matrix, dist_coeff):
        self.rvec, self.tvec, _ = aruco.estimatePoseSingleMarkers(self.corners, self.marker_size(), cam_matrix, dist_coeff)
        return (self.rvec, self.tvec)
    
    # Allows you to manually set where a marker is, for use on board positions only.
    def set_board_position(self, board_position):
        if self.marker_type != "anchor":
            raise Exception("Attempted to set a piece's board position, which is not allowed. Use to_board_position to calculate the piece's position relative to anchor markers.")
        self.exact_board_position = board_position

    # Return if rvec, tvec, and board_position set
    def fully_defined(self):
        return self.rvec == "not calculated" or self.tvec == "not calculated" or self.exact_board_position == "not calculated" or self.closest_board_position == "not calculated"

    # Converts my world coordinates to a board position given some information about the board and the locations of the markers.
    # anchor_markers is two or more anchor arucos used as reference points.
    def to_board_position(self, anchor_markers: List[ArucoInfo]):
        if len(anchor_markers) < 2:
            raise Exception("You must provide at least 2 ArucoInfo objects for anchors to calculate a board position.")

        # Verify that:
        # - Each anchor_marker is an "anchor"
        # - Each anchor_marker has its rvec, tvec, and board_position set
        for marker_data in anchor_markers:
            if marker_data.type != "anchor":
                raise Exception("A marker in anchor_markers is not an anchor.")
            if not marker_data.fully_defined():
                raise Exception("A marker in anchor_markers is not fully defined (call to_world_coordinates and set_board_position on each anchor)")

        # We use each anchor to extract an approximate board position, then average and round at the end.
        pos_estimates = []

        for marker_data in anchor_markers:
            # Redefine the piece's pose in terms of the chosen anchor.
            _, rebased_tvec = ArucoInfo.change_basis(marker_data.rvec, marker_data.tvec, self.rvec, self.tvec)
            
            # Use the tvec to get a board position.
            this_pos_estimate = (rebased_tvec[0] / self.SPACE_WIDTH, rebased_tvec[1] / self.SPACE_WIDTH)
            pos_estimates.append(this_pos_estimate)

        # Save the exact (decimal) board pos in case we need it.
        self.exact_board_position = (sum(x for x, y in pos_estimates) / len(pos_estimates), sum(y for x, y in pos_estimates) / len(pos_estimates))

        # Average and round to an integer space.
        self.closest_board_position = (round(self.exact_board_position[0]), round(self.exact_board_position[1]))

        return self.closest_board_position
    
    # Changes the basis of the second rvec, tvec to be in the first.
    def change_basis(rvec1, tvec1, rvec2, tvec2):
        # Convert rvecs to a rotation matrix
        R1, _ = cv2.Rodrigues(rvec1)
        R2, _ = cv2.Rodrigues(rvec2)
        
        # Step 1: Translate tvec2 into the new coordinate system by subtracting tvec1
        tvec2_new = tvec2 - tvec1
        
        # Step 2: Rotate the new translation vector using the inverse of R1
        # Multiply the translation by the inverse of R1 (the inverse of a rotation matrix is its transpose)
        R1_inv = R1.T 
        
        # Apply the rotation
        tvec2_new_rotated = R1_inv.dot(tvec2_new)
        
        # Step 3: Rotate rvec2 to the new coordinate system
        rvec2_new = R1_inv.dot(R2) 
        
        # Convert the new rvec2 back to a Rodrigues rotation vector
        rvec2_new, _ = cv2.Rodrigues(rvec2_new)
        
        return rvec2_new, tvec2_new_rotated
    
    def __str__(self):
        if self.fully_defined():
            return f"DEFINED ArucoInfo ID {self.id} ({self.type}); corners @ {self.corners}; rvec {self.rvec}, tvec {self.tvec}; board position {self.exact_board_position} ({self.closest_board_position})"
        return f"PARTIAL ArucoInfo ID {self.id} ({self.type}); corners @ {self.corners}; rvec {self.rvec}, tvec {self.tvec}; board position {self.exact_board_position} ({self.closest_board_position})"