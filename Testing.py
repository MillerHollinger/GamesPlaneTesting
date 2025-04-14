# Entry point for testing the system.

from Games.TicTacToe import TicTacToe
import argparse
import imutils
import cv2

# Create an instance of the game.
game = TicTacToe("./example-calibration.yaml")
print(f"Starting instance of {game.name}")

# Read in the picture.
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="Path to image with ARUCO tag(s).")
args = vars(ap.parse_args())
print("Processing image " + args["image"])

# Rescale the image.
# Note: At high image sizes, accuracy lowers.
IMAGE_SCALE = 400
image = cv2.imread(args["image"])
image = imutils.resize(image, width=IMAGE_SCALE)

# Get the DigitalArucos from this picture.
pieces, anchors = game.process_image(image)

for info in pieces + anchors:
    info.put_summary_graphic(image)
    info.put_bounds(image)


cv2.imshow("Image", image)
cv2.waitKey(0)