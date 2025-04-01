# Entry point for testing the system.

from DummyGame import *

# Create an instance of the game.
game = DummyGame()
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

print(pieces[0])