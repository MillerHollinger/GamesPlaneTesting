# This is a dummy file that shows how you can use the GamesPlane pipeline to construct a board and game, and get information about pictures.

from GamesFrame import *
from PhysicalBoardInfo import *
from PhysicalAruco import *

# Define the arucos for this GamesPlane.
black_piece_arucos = PhysicalAruco.generate_many(
    [1, 2, 3, 4, 5], 
    "black", 
    1.66,
    False,
    [None for i in range(5)]
)
white_piece_arucos = PhysicalAruco.generate_many(
    [6, 7, 8, 9, 10], 
    "black", 
    1.66,
    False,
    [None for i in range(5)]
)
anchor_arucos = PhysicalAruco.generate_many(
    [11, 12, 13, 14, 15], 
    "anchor", 
    5.05,
    True,
    [(-1, 5), (5, 5), (-1, -1), (5, -1), (2, -2)]
)

# Set up where pieces may be.
valid_board_pos = [[(x, y) for y in range(5)] for x in range(5)]

# Create the physical board.
board_info = PhysicalBoardInfo(black_piece_arucos + white_piece_arucos, anchor_arucos, valid_board_pos, 5.05)

# Set up the GamesFrame for the board.
gframe = GamesFrame("./calib-dummy.yaml", board_info)

# Set 