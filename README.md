# GamesPlane
Welcome to GamesPlane, Gamesman's step into the next dimension.  
GamesPlane connects a real-life game board to Gamesman using your phone's camera, recording your game's history and showing you the next best moves.

# How to Set Up a Game
To set up a game, you need a **GamesPlane** and a **GamesFrame**.  
A **GamesPlane** is a special board compatible with this system.  
You can use essentially any normal game board as a GamesPlane by adding ArUco markers.

A **GamesFrame** contains basic information about a game, including:
- Name of the game
- ArUcos in use in the game, and info about each ArUco
- Board shape
- Camera information

What follows is an example of building a GamesPlane and GamesFrame for  tic-tac-toe.

## Step 1: Preparing the GamesPlane
Before you can start coding, you'll need an actual board to play on! Compatible boards are called GamesPlanes.  
You'll place **anchor** markers on the board that help the camera locate your pieces. Then, you can place **unanchored** markers on pieces, which will be located by the software.  

To prepare your GamesPlane:
1. Print out your ArUco Classic markers.
    - Each piece needs one marker. The board needs at least one, but more board markers leads to higher accuracy.
    - Each marker needs a white border.
    - Different sizes of marker are supported. (For example, your pieces could have smaller markers than your board anchor markers)
    - Be sure to plan which ArUco will go where, as this will make setting up your GamesFrame easier. (For example, for Tic-Tac-Toe, you might plan ArUco IDs 1, 2, and 3 to put around the board, and ArUco IDs 4 though 12 as pieces)
2. Tape your markers to your board and pieces.
    - Tape one ArUco marker to each piece.
    - Tape your board markers onto the board.


Your GamesPlane is now ready! Now, let's set up the GamesFrame.

## Step 2: Preparing the GamesFrame
A GamesFrame holds important information about your board that is used to solve for piece positions.

1. Create a new file. For our example, we'll call it TicTacToeGame.py.
```python
from GamesFrame import *
from PhysicalBoardInfo import *
from PhysicalAruco import *

class TicTacToe:
    def __init__(self, camera_yaml):
        self.name = "Tic Tac Toe"
        return
```
2. Let's set up the Physical Aruco information. PhysicalAruco represents an actual ArUco that you taped to the board or a piece. Each has 5 variables:  
**PhysicalAruco**
    - id : Which ArUco ID this object represents.
    - tag : What kind of marker this is. For Tic-Tac-Toe, we'll have "X", "O", and "anchor".
    - size : How long in centimeters a side is.
    - anchored : True if this ArUco is taped down and fixed in place. False if it's on a mobile piece.
    - board_position : If anchored, board_position is an (x, y) tuple of where on the board the anchor is. Leave it empty if it's unanchored.  

Let's imagine we set up 3 anchor arucos and 9 piece arucos, with the anchors being IDs 1, 2, and 3, and the pieces being 4 through 12.   
We then taped our anchor arucos below the bottom-left square, above the top-middle square, and to the right of the bottom-right square. 
<!-- TODO: Add pictures to better explain the above. --> 
To define the arucos, we'd add:
```py 
# Define our PhysicalArucos. We use .generate_many, a collectivized version of the constructor, to repeat less.
anchor_arucos = PhysicalAruco.generate_many(
    [1, 2, 3], # ArUco IDs 1, 2, 3.
    "anchor",  # We tag these as "anchor."
    5.05, # 5.05 cm to a side.
    True, # It is stuck in place.
    [(0, -1), (1, 3), (3, 0)] # Make sure to get the order right for these positions! They map onto the above ID list, i.e. ID 1 is position 
)
x_arucos = PhysicalAruco.generate_many(
    [4, 5, 6, 7, 8], # ArUco IDs 4 to 8.
    "X", # Call it "X" 
    1.66, # These are smaller, just 1.66 cm to a side.
    False, # Not stuck in place.
    [None for i in range(5)] # They're not stuck in place, so empty.
)
o_arucos = PhysicalAruco.generate_many(
    [9, 10, 11, 12], # ArUco IDs 9 to 12.
    "O", # Call it "X" 
    1.66, # 1.66 cm to a side.
    False, # Not stuck in place.
    [None for i in range(4)] # They're not stuck in place, so empty.
)
        
```


Now is a good time to explain camera coordinates, world coordinates, and board coordinates.
- Camera Coordinates: (x, y) format. These represent a pixel in your picture.
- World Coordinates: (x, y, z) foramt. These represent a specific point in space, with the camera's point in space as the origin.
- Board Coordinates: (x, y) format. This represents a specific location on your game board.  

For each anchor ArUco taped to your board, you'll need to defined a board position.  
In Tic-Tac-Toe, we might decide to call the bottom-left square (0, 0), making the top-right square (2, 2).  
If you placed an anchor directly below the bottom-left square, it would then be at (0, -1).

<!-- TODO: Add pictures to better explain the above. -->

3. Now, let's define where pieces can be on the board. It's Tic-Tac-Toe, so they can be in the 3x3 grid in the center of the board.
```py
valid_positions = [(x, y) for x in range(3) for y in range(3)]
```

4. Let's feed our PhysicalAruco information and our list of valid positions into a PhysicalBoardInfo object, which stores them all together.  
```py
# Create the physical board.
board_info = PhysicalBoardInfo(
    x_arucos + o_arucos, # The pieces.
    anchor_arucos, # The anchors.
    valid_positions, # The 3x3 grid that pieces can be placed in.
    5.05 # How we convert from centimeters to board units (5.05 cm to a space)
)
```

5. Last step -- create a GamesFrame with our camera's yaml calibration matrix, which will be passed in with the constructor.
```py
self.gframe = GamesFrame(camera_yaml, board_info)
```

Our GamesFrame is ready to go! Now we can use it on an image to locate pieces.

## Step 3: Getting Data from Images
You can use `game.gframe.process_image(image)` on an image to extract information from it.
```py
# Create an instance of the game using the camera calibration file.
game = TicTacToe("./calib-dummy.yaml")

# Read in the picture.
image = cv2.imread("./test-image.jpg")

# Get the DigitalArucos from this picture.
pieces, anchors = game.gframe.process_image(image)
```

There you go! `pieces` and `anchors` now contain information about the aruco markers, stored in DigitalAruco format.  
Each DigitalAruco object has many useful fields, most importantly:
- `closest_board_position` : Where the ArUco is estimated to be located in board space, which is why we did all this stuff. This will be (1, 1) if the piece is placed in the center of our Tic-Tac-Toe board.
- `top_r`, `top_l`, `bot_r`, `bot_l`, `center` : Where the corners of the ArUco are in camera coordinates. Great for rendering information to the source image!


```py
# Show the information.
for info in pieces + anchors:
    info.put_summary_graphic(image) # This adds text to the image about the ArUco.
    info.put_bounds(image) # This draws the ArUco's bounds onto the image.

cv2.imshow("Image", image)
cv2.waitKey(0)
```

