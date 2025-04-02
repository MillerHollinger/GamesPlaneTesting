# This is a dummy file that shows how you can use the GamesPlane pipeline to construct a board and game, and get information about pictures.

from Helpers.GamesFrame import *
from Helpers.PhysicalBoardInfo import *
from Helpers.PhysicalAruco import *
from .GamesPlaneGame import *

class Beeline(GamesPlaneGame):
    def __init__(self, camera_yaml):

        self.name = "Beeline"

        # Define the arucos for this GamesPlane.
        blue_bees = PhysicalAruco.generate_many(
            [1, 2, 3], 
            "black", 
            1.66,
            False,
            [None for i in range(3)]
        )
        red_bees = PhysicalAruco.generate_many(
            [4, 5, 6], 
            "white", 
            1.66,
            False,
            [None for i in range(3)]
        )
        anchors = PhysicalAruco.generate_many(
            [11, 12, 13, 14], 
            "anchor", 
            5.05,
            True,
            [(-5.2, 0), (5.2, 0), (-5.2, 6), (5.2, 6)]
        )

        # Set up where pieces may be.
        valid_board_pos = [
            [0, 0],
            [0, 2],
            [0, 4],
            [0, 6],
            [1.73, 1],
            [1.73, 3],
            [1.73, 5],
            [3.46, 2],
            [3.46, 4],
            [5.20, 3],
            [-1.73, 1],
            [-1.73, 3],
            [-1.73, 5],
            [-3.46, 2],
            [-3.46, 4],
            [-5.20, 3]
        ]

        # Create the physical board.
        board_info = PhysicalBoardInfo(blue_bees + red_bees, anchors, valid_board_pos, 1.95)

        # Set up the GamesFrame for the board.
        self.gframe = GamesFrame(camera_yaml, board_info)

        # We're good to go. Now we can feed in images to the gframe using .process_image.

    # Shortcut to pass an image to the gframe.
    def process_image(self, image):
        return self.gframe.process_image(image)
    
    # DEBUG Helper for now. Returns a text-based representation of the board.
    def to_board(self, pieces: list[DigitalAruco]):
        result = [["-" for x in range(5)] for y in range(5)]
        for piece in pieces:
            pos = piece.closest_board_position
            result[pos[0]][pos[1]] = piece.phys.tag[0]
            
        return result