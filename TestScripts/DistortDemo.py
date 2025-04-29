import cv2
import numpy as np

def warp_and_overlay(background, foreground, dst_points):
    """
    Warps the foreground image to the given four destination points
    and overlays it onto the background image.

    Parameters:
        background (np.ndarray): The background image.
        foreground (np.ndarray): The foreground image to be transformed.
        dst_points (np.ndarray): 4x2 array of destination points in (x, y) order.

    Returns:
        np.ndarray: The background image with the warped foreground overlaid.
    """
    h, w = foreground.shape[:2]

    # Source points from the foreground image corners
    src_points = np.float32([
        [0, 0],
        [w - 1, 0],
        [w - 1, h - 1],
        [0, h - 1]
    ])

    dst_points = np.float32(dst_points)

    # Compute the perspective transform matrix
    M = cv2.getPerspectiveTransform(src_points, dst_points)

    # Warp the foreground image to the destination quadrilateral
    warped = cv2.warpPerspective(foreground, M, (background.shape[1], background.shape[0]))

    # Add alpha channel to background
    #alpha = np.full((background.shape[0], background.shape[1], 1), 255, dtype=np.uint8)
    #background = np.concatenate((background, alpha), axis=2)

    # Create a mask from the warped image
    warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(warped_gray, 1, 255, cv2.THRESH_BINARY)

    # Invert the mask for background
    mask_inv = cv2.bitwise_not(mask)

    # Black-out the area of the warped image in the background
    background_area = cv2.bitwise_and(background, background, mask=mask_inv)

    # Take only the warped image region
    warped_area = cv2.bitwise_and(warped, warped, mask=mask)

    # Add the two together
    result = cv2.add(background_area, warped_area)

    return result

def create_horizontal_gradient(width, height, start_color, end_color):
    """
    Create a horizontal gradient image from start_color to end_color with an alpha channel.

    Parameters:
        width (int): Width of the image.
        height (int): Height of the image.
        start_color (tuple): BGR start color (e.g., (255, 255, 255)).
        end_color (tuple): BGR end color (e.g., (255, 0, 0)).

    Returns:
        np.ndarray: BGRA image with horizontal gradient and full opacity.
    """
    # Create linear gradients for B, G, R channels
    b = np.linspace(start_color[0], end_color[0], width, dtype=np.uint8)
    g = np.linspace(start_color[1], end_color[1], width, dtype=np.uint8)
    r = np.linspace(start_color[2], end_color[2], width, dtype=np.uint8)
    a = np.full(width, 255, dtype=np.uint8)  # Full opacity

    # Stack the 1D channel arrays into (width, 4)
    gradient_row = np.stack([b, g, r, a], axis=1)

    # Repeat the row for the full height
    gradient_image = np.tile(gradient_row, (height, 1, 1))

    return gradient_image

# Example usage:
if __name__ == "__main__":
    width, height = 600, 300
    start_color = (255, 255, 255)  # White in BGR
    end_color = (255, 0, 0)        # Blue in BGR

    white_to_blue = create_horizontal_gradient(width, height, start_color, end_color)

    # Red to Black gradient
    start_color = (0, 0, 255)  # Red in BGR
    end_color = (0, 0, 0)      # Black in BGR

    red_to_black = create_horizontal_gradient(width, height, start_color, end_color)

    overlaid = warp_and_overlay(white_to_blue, red_to_black, np.array(((0, 0), (100, 0), (100, 100), (0, 100))))

    cv2.imshow('Gradient', overlaid)
    cv2.waitKey(0)
    cv2.destroyAllWindows()