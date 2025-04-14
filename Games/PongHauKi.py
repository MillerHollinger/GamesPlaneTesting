# This is a dummy file that shows how you can use the GamesPlane pipeline to construct a board and game, and get information about pictures.

from Helpers.GamesFrame import *
from Helpers.PhysicalBoardInfo import *
from Helpers.PhysicalAruco import *
from .GamesPlaneGame import *

class PongHauKi(GamesPlaneGame):
    def __init__(self, camera_yaml):

        self.name = ""

        # Define the arucos for this GamesPlane.
        anchor_arucos = PhysicalAruco.generate_many(
            [12, 13, 14, 15], 
            "anchor", 
            5.08,
            True, # Anchored?
            [(-4, 2.8), (-4, -2.8), (4, 2.8), (4, -2.8)]
        )

        # Define the arucos for this GamesPlane.
        pieces_aruco = PhysicalAruco.generate_many(
            [3, 5], 
            "piece", 
            1.66,
            False, # Anchored?
            [None for i in range(2)]
        )

        # Set up where pieces may be.
        valid_board_pos = [(-2.2, 2.7), (2.2, 2.7), (2.2, -2.2), (-2.2, -2.2), (0,0)]

        # Create the physical board.
        board_info = PhysicalBoardInfo(pieces_aruco, anchor_arucos, valid_board_pos, 5.08)

        # Set up the GamesFrame for the board.
        self.gframe = GamesFrame(camera_yaml, board_info)

        # We're good to go. Now we can feed in images to the gframe using .process_image.

    # Shortcut to pass an image to the gframe.
    def process_image(self, image):
        return self.gframe.process_image(image)
