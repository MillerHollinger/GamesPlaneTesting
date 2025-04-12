from Helpers.GamesFrame import *
from Helpers.PhysicalBoardInfo import *
from Helpers.PhysicalAruco import *
from .GamesPlaneGame import *

class TicTacToe(GamesPlaneGame):
    def __init__(self, camera_yaml):
        self.name = "Tic Tac Toe"

        # Define our PhysicalArucos. We use .generate_many, a collectivized version of the constructor, to repeat less.
        anchor_arucos = PhysicalAruco.generate_many(
            [10, 11, 12, 13], # ArUco IDs 1, 2, 3.
            "anchor",  # We tag these as "anchor."
            5, # 5.05 cm to a side.
            True, # It is stuck in place.
            [(-1, 2), (3, 2), (-1, 0), (3, 0)] # Make sure to get the order right for these positions! They map onto the above ID list, i.e. ID 1 is position 
        )
        x_arucos = PhysicalAruco.generate_many(
            [1], # ArUco IDs 4 to 8.
            "X", # Call it "X" 
            3, # These are smaller, just 1.66 cm to a side.
            False, # Not stuck in place.
            [None] # They're not stuck in place, so empty.
        )
        o_arucos = PhysicalAruco.generate_many(
            [2], # ArUco IDs 9 to 12.
            "O", # Call it "X" 
            3, # 1.66 cm to a side.
            False, # Not stuck in place.
            [None] # They're not stuck in place, so empty.
        )

        valid_positions = [(x, y) for x in range(3) for y in range(3)]

        # Create the physical board.
        board_info = PhysicalBoardInfo(
            x_arucos + o_arucos, # The pieces.
            anchor_arucos, # The anchors.
            valid_positions, # The 3x3 grid that pieces can be placed in.
            5 # How we convert from centimeters to board units (5.05 cm to a space)
        )

        self.gframe = GamesFrame(camera_yaml, board_info)

        return
    
    def process_image(self, image):
        return self.gframe.process_image(image)