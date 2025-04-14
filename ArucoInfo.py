# The ArucoInfo class stores data about an Aruco marker.
# Miller Hollinger 2025

import cv2
from cv2 import aruco
import numpy as np

RED = (0, 255, 0)
GREEN = (0, 0, 255)
BLUE = (255, 0, 0)
WHITE = (255, 255, 255)
CYAN = (255, 255, 0)


class ArucoInfo:
    # raw_corners: of the aruco stored in this order:
        # 1 2
        # | |
        # 4 3
    # marker_type: represents marker representations:
    VALID_MARKER_TYPES = ["anchor", "white", "black"]
    # In cm, how wide a square space on the board is.
    space_width = 5.05
    

    def __init__(self, id, raw_corners, marker_type, cam_matrix, dist_coeff):
        if raw_corners.shape != (1, 4, 2):
            raise Exception(f"{raw_corners.shape = } but should be (1, 4, 2)")
        if marker_type not in self.VALID_MARKER_TYPES:
            raise Exception(f"{marker_type = } but should be in {self.VALID_MARKER_TYPES}")
        
        self.id = id
        self.raw_corners = raw_corners
        self.marker_type = marker_type
        self.cam_matrix = cam_matrix
        self.dist_coeff = dist_coeff
        # Reshape corners for easier use in UI.
        self.reshaped = self.raw_corners.reshape((4, 2))
        
        # Convert coordinate pairs to integers.
        self.int_corners = [(int(x[0]), int(x[1])) for x in self.reshaped]
        self.top_l, self.top_r, self.bot_r, self.bot_l = self.int_corners
        self.center = [int(np.mean(self.reshaped[:, i])) for i in [0, 1]]

        # World coordinates are not yet calculated.
        # rvec is Rodrigues' rotation vector form of the aruco's rotation.
        # tvec is the offset from the camera.
        self.rvec, self.tvec = None, None

        # Board position is not yet calculated.
        self.exact_board_position = None
        self.closest_board_position = None


    # Debug
    def show_init(self, image):
        icopy = image.copy()
        for corner in self.int_corners:
             cv2.circle(icopy, corner, 5, GREEN, -1)
        cv2.circle(icopy, self.center, 5, RED, -1)
        cv2.putText(icopy, self.marker_type, self.center, 0, 0.5, WHITE)
        cv2.imshow(f"[ArucoInfo] parameters for ID={self.id}", icopy)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    # Converts ArucoInfo coords to world coords using
    # cam_matrix and dist_coeff. Stores rvec and tvec.
    def to_world_coordinates(self, debug=None):

        if self.marker_type == "anchor":
            self.size = self.space_width
        elif self.marker_type in ["white", "black"]:
            self.size = 1.66
        
        self.rvec, self.tvec, _ = aruco.estimatePoseSingleMarkers(
            self.raw_corners, self.size, self.cam_matrix, self.dist_coeff)
        self.tvec = self.tvec[0][0]

        # Debug
        icopy = debug.copy()
        if debug is not None:
            axis = np.float32([[0,0,0], [1,0,0], [0,1,0], [0,0,1]]) * self.size
            ppts, _ = cv2.projectPoints(axis, self.rvec, self.tvec, self.cam_matrix, self.dist_coeff)
            o, x, y, z = ppts.astype(int).reshape(-1, 2)
            
            cv2.arrowedLine(icopy, o, x, RED,   2)
            cv2.arrowedLine(icopy, o, y, GREEN, 2)
            cv2.arrowedLine(icopy, o, z, BLUE,  2)
            cv2.putText(icopy, self.marker_type, o, 0, 0.5, WHITE)
        print(f"World coords for ID={self.id} are {self.tvec}")
        return icopy


    def plot_board_coordinates(self, other, board_positions, debug=None):
        if "anchor" not in [self.marker_type, other.marker_type]:
            raise Exception("One marker must be an anchor")
        
        if self.marker_type == "anchor":
            anchor, piece = self, other
        else:
            anchor, piece = other, self
        if anchor.rvec is None:
            anchor.to_world_coordinates()
        if piece.rvec  is None:
            piece.to_world_coordinates()
        
        # In WORLD coords
        delta_xyz = piece.tvec - anchor.tvec
        print(f"Delta from A (ID={anchor.id}) to P (ID={piece.id}): {delta_xyz}")
        rotation_matrix, _ = cv2.Rodrigues(anchor.rvec)

        # In BOARD coords
        delta_anchor_frame = np.dot(rotation_matrix.T, delta_xyz)
        anchor_pos = board_positions[anchor.id]
        # In BOARD coords
        scale = 1 / anchor.space_width
        piece_pos = (
            float("{:.1f}".format(anchor_pos[0] + delta_anchor_frame[0] * scale)),
            float("{:.1f}".format(anchor_pos[1] + delta_anchor_frame[1] * scale))
        )
        # Debug
        icopy = debug.copy()
        if debug is not None:
            ac0, ac1 = anchor.center
            pc0, pc1 = piece.center
            cv2.arrowedLine(icopy, (ac0, ac1), (pc0, pc1), WHITE, 2, tipLength=0.1)
            cv2.putText(icopy, f"{anchor_pos}", (ac0, ac1 - 20), 0, 0.5, CYAN, 2)
            cv2.putText(icopy, f"{piece_pos}",  (pc0, pc1 - 20), 0, 0.5, CYAN, 2)
        return icopy

    ### old code ###
    
    # Allows you to manually set where a marker is, for use on board positions only.
    def set_board_position(self, board_position):
        if self.type != "anchor":
            raise Exception("Attempted to set a piece's board position, which is not allowed. Use to_board_position to calculate the piece's position relative to anchor markers.")
        self.exact_board_position = board_position
        self.closest_board_position = board_position

    # Return if rvec, tvec, and board_position set
    def fully_defined(self):
        return (not isinstance(self.rvec, list)) \
            or (not isinstance(self.tvec, list)) \
            or (self.exact_board_position == "not calculated") \
            or (self.closest_board_position == "not calculated")

    # Converts my world coordinates to a board position given some information about the board and the locations of the markers.
    # anchor_markers is two or more anchor arucos used as reference points.
    def to_board_position(self, anchor_markers):
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
            print(f"Locating Piece {self.id}: Anchor {marker_data.id} says an offset of {rebased_tvec}")
            
            # Use the tvec to get a board position.
            this_pos_estimate = [rebased_tvec[0] / self.space_width, rebased_tvec[2] / self.space_width]

            # Offset by the anchor's place.
            this_pos_estimate[0] += marker_data.closest_board_position[0]
            this_pos_estimate[1] += marker_data.closest_board_position[1]

            pos_estimates.append(this_pos_estimate)

            print(f"Locating Piece {self.id}: Anchor {marker_data.id} estimates at {this_pos_estimate}")

        # Save the exact (decimal) board pos in case we need it.
        self.exact_board_position = (sum(x for x, z in pos_estimates) / len(pos_estimates), sum(z for x, z in pos_estimates) / len(pos_estimates))

        # Average and round to an integer space.
        self.closest_board_position = (round(self.exact_board_position[0]), round(self.exact_board_position[1]))

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
        if self.fully_defined():
            return f"DEFINED ArucoInfo ID {self.id} ({self.type}); center @ {self.center}; rvec {self.rvec}, tvec {self.tvec}; board position {self.closest_board_position} ({self.exact_board_position})"
        return f"PARTIAL ArucoInfo ID {self.id} ({self.type}); center @ {self.center}; rvec {self.rvec}, tvec {self.tvec}; board position {self.closest_board_position} ({self.exact_board_position})"
