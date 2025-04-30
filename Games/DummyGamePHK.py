# This is a dummy file that shows how you can use the GamesPlane pipeline to construct a board and game, and get information about pictures.

from Helpers.GamesFrame import *
from Helpers.PhysicalBoardInfo import *
from Helpers.PhysicalAruco import *
from .GamesPlaneGame import *

class DummyGame(GamesPlaneGame):
    def __init__(self, camera_yaml):

        self.name = "Pong Hau K'i"

        # Set up aruco info 

        # Define the arucos for this GamesPlane.
        
        
        pieces_arucos = PhysicalAruco.generate_many(
            [8, 9, 10, 11], 
            "white", 
            1.23,
            False,
            [None for i in range(4)]
        )
        

        anchor_arucos = PhysicalAruco.generate_many(
            [12, 13, 14, 15], 
            "anchor", 
            5.08,
            True,
            [(-4, 2.8), (-4, -2.8), (4, 2.8), (4, -2.8)]
        )

        # Set up where pieces may be.
        valid_board_pos = [(-2.2, 2.7), (2.2, 2.7), (2.2, -2.2), (-2.2, -2.2), (0, 0)]

        # Create the physical board.
        board_info = PhysicalBoardInfo(pieces_arucos, anchor_arucos, valid_board_pos, 5.08)

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