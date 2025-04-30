# This is a dummy file that shows how to use the GamesPlane pipeline
# to construct a board and game, and get information about pictures.

from Helpers.GamesFrame import *
from Helpers.PhysicalBoardInfo import *
from Helpers.PhysicalAruco import *
from .GamesPlaneGame import *

SPACE_SIZE = 4.88   # cm
PIECE_SIZE = 1.66   # cm
GRID = 3            # 3x3

class DummyGame(GamesPlaneGame):
    def __init__(self, camera_yaml):
        self.name = "TicTacToe"

        # Define the arucos for this GamesPlane.
        X_arucos = PhysicalAruco.generate_many(
            [8, 9], 
            "X", 
            PIECE_SIZE,
            False,
            [None, None]
        )
        O_arucos = PhysicalAruco.generate_many(
            [10, 11], 
            "O", 
            PIECE_SIZE,
            False,
            [None, None]
        )
        anchor_arucos = PhysicalAruco.generate_many(
            [12, 13, 14, 15], 
            "anchor", 
            SPACE_SIZE,
            True,
            [(-1, 2), (-1, 0), (3, 2), (3, 0)]
        )

        # Set up where pieces may be.
        valid_board_pos = [(x, y) for y in range(GRID) for x in range(GRID)]

        # Create the physical board.
        board_info = PhysicalBoardInfo(X_arucos + O_arucos, 
                        anchor_arucos, valid_board_pos, SPACE_SIZE)

        # Set up the GamesFrame for the board.
        self.gframe = GamesFrame(camera_yaml, board_info)

    # Shortcut to pass an image to the gframe.
    def process_image(self, image, reason=True):
        return self.gframe.process_image(image, reason)
    
    # DEBUG Helper for now. Returns a text-based representation of the board.
    def to_board(self, pieces: list[DigitalAruco]):
        board = [["-" for x in range(GRID)] for y in range(GRID)]
        result = ""

        for piece in pieces:
            x, y = piece.closest_board_position
            board[y][x] = piece.phys.tag[0] # first char
        for row_y in board:
            result += "".join(row_y) + "\n"
        return result