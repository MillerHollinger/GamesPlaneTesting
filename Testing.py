# Entry point for testing the system.

from Games.DummyGame import *

# Create an instance of the game.
game = DummyGame("./example-calibration.yaml")
print(f"Starting instance of {game.name}")

# Read in the picture.
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="Path to image with ARUCO tag(s).")
args = vars(ap.parse_args())
print("Processing image " + args["image"])

# Rescale the image to a given value. 
# Larger values run slower but higher accuracy likely.
IMAGE_SCALE = 800
image = cv2.imread(args["image"])
image = imutils.resize(image, width=IMAGE_SCALE)

# Get the DigitalArucos from this picture.
pieces, anchors = game.process_image(image)

for info in pieces + anchors:
    info.put_summary_graphic(image)
    info.put_bounds(image)

"""
to_board = game.to_board(pieces)
for y in range(4, -1, -1):
    result = ""
    for x in range(0, 5):
        result = result + str(to_board[x][y])
    print(result)
"""

cv2.imshow("Image", image)
cv2.waitKey(0)