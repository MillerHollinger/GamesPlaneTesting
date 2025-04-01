# Stores the data about a specific GamesPlane board.
# This includes where the arucos are, where pieces may be placed, and how many cm translates to one space unit.

from PhysicalAruco import PhysicalAruco
import numpy as np

class PhysicalBoardInfo:
    def __init__(self, unanchored_arucos: list[PhysicalAruco], anchored_arucos: list[PhysicalAruco], valid_board_positions: list[(float, float)], cm_to_space: float = 0):
        if len(unanchored_arucos) == 0:
            raise Exception("PhysicalBoardInfo: You must supply at least one unanchored_aruco.")
        if len(anchored_arucos) == 0:
            raise Exception("PhysicalBoardInfo: You must supply at least one anchored_aruco.")
        if len(valid_board_positions) == 0:
            raise Exception("PhysicalBoardInfo: You must supply at least one valid board position.")
        if cm_to_space <= 0:
            raise Exception("PhysicalBoardInfo: cm_to_space must be greater than 0.")
        
        # The arucos associated with this board.
        self.unanchored_arucos = unanchored_arucos
        self.anchored_arucos = anchored_arucos

        # Where pieces may be located on the board, in board units.
        self.valid_board_positions = valid_board_positions

        # How many cm converts to one board unit.
        self.cm_to_space = cm_to_space

        return
    
    # Given an id, returns its PhysicalAruco information.
    def aruco_info_for(self, id):
        for aru in self.unanchored_arucos + self.anchored_arucos:
            if aru.id == id:
                return aru

        raise Exception(f"PhysicalBoardInfo: ArUco ID {id} does not exist in this context.")

    # Given an X, Y board position (in board units, not cm), returns the closest valid_board_position.
    def closest_valid_space(self, board_position):
        if len(self.valid_board_positions) == 1:
            return self.valid_board_positions[0]

        min_distance = 9999999
        closest_pos = None
        for pos in self.valid_board_positions[0:]:
            distance = np.linalg.norm(np.array(board_position) - np.array(pos))
            if distance < min_distance:
                min_distance = distance
                closest_pos = pos

        return closest_pos