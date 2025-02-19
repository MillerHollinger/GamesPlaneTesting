# Aruco tracking
# from https://pyimagesearch.com/2020/12/21/detecting-aruco-markers-with-opencv-and-python/

# import the necessary packages
import argparse
import imutils
import cv2
import sys

# Construct argument parser.
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="Path to input image containing ArUCo tag.")
args = vars(ap.parse_args())

# We're using the original aruco dict.
DICT = cv2.aruco.DICT_ARUCO_ORIGINAL

# Load and resize image.
print("Loading image...")
image = cv2.imread(args["image"])
image = imutils.resize(image, width=600)

# Set up ARUCO parameters.
arucoDict = cv2.aruco.getPredefinedDictionary(DICT)
arucoParams = cv2.aruco.DetectorParameters()

# Detect the markers.
(corners, ids, rejected) = cv2.aruco.detectMarkers(image, arucoDict,
	parameters=arucoParams)

# Render markers.
if len(corners) > 0:
	# Flatten ARUCO IDs list
	ids = ids.flatten()
	
	# Render each ARUCO bounding box
	for (markerCorner, markerID) in zip(corners, ids):
		# Read marker corners.
		corners = markerCorner.reshape((4, 2))
		(topLeft, topRight, bottomRight, bottomLeft) = corners
		
		# Convert coordinate pairs to ints.
		topRight = (int(topRight[0]), int(topRight[1]))
		bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
		bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
		topLeft = (int(topLeft[0]), int(topLeft[1]))
		
		# Draw bounding box.
		cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
		cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
		cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
		cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)
		
		# Draw center point.
		# cX = int((topLeft[0] + bottomRight[0]) / 2.0)
		# cY = int((topLeft[1] + bottomRight[1]) / 2.0)
		# cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)
		
		# Add ARUCO ID
		cv2.putText(image, str(markerID),
			(topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
			0.5, (0, 255, 0), 2)
		print("Found ARUCO ID: {}".format(markerID))
		
		# Show on image
		# TODO Just show the final image, don't show each one-by-one.
		cv2.imshow("Image", image)
		cv2.waitKey(0)
		
"""
HOW TO TURN ARUCO DATA INTO POSITIONS

https://stackoverflow.com/questions/68019526/how-can-i-get-the-distance-from-my-camera-to-an-opencv-aruco-marker
https://docs.opencv.org/4.x/dd/d1f/structcv_1_1aruco_1_1EstimateParameters.html
https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#ga549c2075fac14829ff4a58bc931c033d

We'll use this to locate each board point and each piece in 3d space.
Then, we can use the two flat dimensions (throwing away height) to define a grid, and place each piece inside the grid.



#######
IGNORE BELOW, OUTDATED
We have the centers of the board arucos and piece arucos.
We  create a grid using the board's arucos.
- TODO Make an algorithm for if we have 1, 2, 3, 4, 5 arucos that lets us easily plug it all in.

The pieces are offset vertically because they have height, so we move the coordinate grid upwards slightly.
- Make this based on how large the board arucos are (which approximates distance).
- Example: If there's only one board aruco visible, and it's huge, we're very close to the board. The grid should move up a lot to compensate.
- What if we're top-down? Then we don't need to move at all. This means we need a way to tell what angle we're looking at the board from.
- If we're top-down, the arucos are squares. If at an angle, they're less square.
- Therefore, we can use the ratio of height to width of each aruco to determine how "glancing" of an angle we're at.
- More glancing angles need more of a height adjustment. Nonglancing angles do not need any adjustment. Scale using that.
- There should probably be an equation for this.

Then, just see where each piece aruco's center falls, and assign it to that space.
If not every piece is spotted, just let the others not update. Reattempt aruco calculation often so this doesn't matter.
- If a piece is missing for several aruco calculations, the UI ought to let you know it's lost track of it.
"""
