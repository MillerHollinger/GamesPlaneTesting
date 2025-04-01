import cv2
import numpy as np

# Load an image or video frame
image = np.zeros((600, 800, 3), dtype=np.uint8)  # Create a black canvas

# Camera intrinsics (example values)
camera_matrix = np.array([[800, 0, 400], [0, 800, 300], [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.zeros(5)  # Assuming no distortion

# Rotation vector (no rotation, just translation)
rvec = np.array([[0.0], [0.0], [0.0]])  # No rotation
tvec = np.array([[0.0], [0.0], [100.0]])  # Move 100 units forward in Z

# Draw the coordinate axes
cv2.drawFrameAxes(image, camera_matrix, dist_coeffs, rvec, tvec, 50)  # Axis length = 50

# Display the image
cv2.imshow("Frame Axes", image)
cv2.waitKey(0)
cv2.destroyAllWindows()