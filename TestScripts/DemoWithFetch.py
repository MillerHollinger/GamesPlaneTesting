# A demo of GamesPlane that fetches board images online
# python -m streamlit run TestScripts/DemoWithFetch.py

import cv2
import sys
sys.path.append(".")
import asyncio
import numpy as np
import streamlit as st
from Games.DummyGameTTT import *
from App.ConvertJSON import fetch_game
from App.BoardFetcher import BoardFetcher
from CameraCalibration.auto_calibration import *
from Helpers.StateEstimator import MajorityEstimator

# 1. CAMERA & GAME
ses = st.session_state
if "camera" not in ses:
    ses.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    yaml_str = get_calib_matrices(cam=ses.camera)
    
    ses.game = fetch_game("Dao", yaml_str)
    ses.fetcher = BoardFetcher("dao", "regular")
    print("CAMERA & GAME SET UP.")

# 2. ONLINE WINDOW
FRAME_WINDOW = st.image([ ])
st.header("Live Feed Debug")
st.subheader("Live Results")
run = st.checkbox("Activate Camera")
data = st.text("Waiting for Camera")
data2 = st.text("")

# 3. HARDCODED X,Y
POS_TO_IDX = {
    2.7 : {
        2.7 : [3, 0],
        0.9 : [3, 1],
        -0.9 : [3, 2],
        -2.7 : [3, 3]
    },
    0.9 : {
        2.7 : [2, 0],
        0.9 : [2, 1],
        -0.9 : [2, 2],
        -2.7 : [2, 3]
    },
    -0.9 : {
        2.7 : [1, 0],
        0.9 : [1, 1],
        -0.9 : [1, 2],
        -2.7 : [1, 3]
    },
    -2.7 : {
        2.7 : [0, 0],
        0.9 : [0, 1],
        -0.9 : [0, 2],
        -2.7 : [0, 3]
    }
}

# 4. HELPER METHODS
async def make_request(board_state):
    asyncio.create_task(st.session_state.fetcher.get_svg_for("1_-----BW--WB-----"))

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
    alpha = np.full((background.shape[0], background.shape[1], 1), 255, dtype=np.uint8)
    background = np.concatenate((background, alpha), axis=2)

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

def overlay_image(background, foreground, x, y):
    """
    Overlay `foreground` onto `background` at position (x, y).
    Handles alpha channel if present.
    
    Args:
        background (np.ndarray): Background image (BGR).
        foreground (np.ndarray): Foreground image (BGRA or BGR).
        x (int): Top-left x position on background.
        y (int): Top-left y position on background.

    Returns:
        np.ndarray: New image with the foreground overlayed on background.
    """
    bg = background.copy()
    
    fg_h, fg_w = foreground.shape[:2]
    #print(f"Image shape {bg.shape[1]} {bg.shape[0]}")

    # Make sure the foreground fits within the background
    if x + fg_w > bg.shape[1] or y + fg_h > bg.shape[0]:
        raise ValueError("Foreground image goes outside the background bounds.")

    # Check if foreground has alpha channel
    if foreground.shape[2] == 4:
        # Split channels
        fg_rgb = foreground[..., :3]
        alpha = foreground[..., 3] / 255.0  # Normalize alpha to [0, 1]
        
        # Extract ROI from background
        roi = bg[y:y+fg_h, x:x+fg_w]

        # Blend the ROI and foreground
        blended = (alpha[..., None] * fg_rgb + (1 - alpha[..., None]) * roi).astype(np.uint8)

        # Replace the ROI on background
        bg[y:y+fg_h, x:x+fg_w] = blended
    else:
        # No alpha channel, just overwrite the region
        bg[y:y+fg_h, x:x+fg_w] = foreground

    return bg

# STATE ESTIMATION
estimator = MajorityEstimator()

# 5. PROCESS VIDEO
while run:
    _, image = ses.camera.read()

    pieces, anchors, reasons = ses.game.process_image(image)
    prefix = f"{len(anchors)} anchors spotted; {len(pieces)} pieces spotted  \n"
    data.write(prefix)# + "  \n".join(["  \n".join([a for a in r]) for r in reasons]))

    for info in pieces + anchors:
        info.put_summary_graphic(image)
        info.put_bounds(image)

    # NOTE: Now try to show the board state.
    # 1. Verify the board state makes sense:
    # - Must find 8 pieces: 4 black, 4 white
    # TODO: Redo to require only one anchor.

    if len(pieces) != 8 or len(anchors) != 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(image)

        print(f"Error: {len(pieces)=}, {len(anchors)=} \n Needs: (8 pieces, 4 anchors) in frame")
        continue    # IGNORE. Has to find 4 anchors

    # 2. Convert board state to board string
    # - For Dao: X is White, O is Black, - is empty
    # - White turn is 1, Black is 2. Assume 1 for now
    # - TODO: How do we say whose turn it is? Button? 
    
    board_str = "1_"
    GRID = len(POS_TO_IDX)
    board_rep = [["-" for c in range(GRID)] for r in range(GRID)]

    for piece in pieces:
        name = "O" if piece.phys.id == 1 else "X"
        pos_x, pos_y = piece.closest_board_position
        idx_x, idx_y = POS_TO_IDX[pos_x][pos_y]
        board_rep[idx_x][idx_y] = name
    
    for r in range(GRID):
        for c in range(GRID):
            board_str += board_rep[c][r]

    # 3. Add board state to state estimator
    estimator.seen_board_state(board_str)
    MIN_FRAMES = 20

    # if len(estimator.queue) > MIN_FRAMES:
    best_state = estimator.curr_board_state()
    data2.write("Estimated board state: " + best_state)

    print("Fetching web image...")
    asyncio.run(ses.fetcher.get_svg_for(best_state))

        correct_order = {
            12: 1,
            13: 4,
            14: 2,
            15: 3
        }
        
        if most_votes in st.session_state.fetcher.board_cache:
            #print("Got an overlay.")
            #image = overlay_image(image, st.session_state.fetcher.board_cache[most_votes], 0, 0)
            #overlay_image = np.full((100, 100, 4), 255, dtype=np.uint8)
            overlay_image = st.session_state.fetcher.board_cache[most_votes]
 
            # TODO Get correct positions to display over.
            display_corners = [a.center for a in sorted(anchors, key=lambda a: correct_order[a.phys.id])]
            #image = overlay_image
            image = warp_and_overlay(image, overlay_image, np.array(display_corners))
            #image = warp_and_overlay(image, st.session_state.fetcher.board_cache[most_votes], np.array(((0, 0), (100, 0), (100, 100), (0, 100))))
            #print(image.shape)
        # 3. Show the current moves suggestion image on top.
        else:
            pass
            #print("Not ready to show an image yet.")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    FRAME_WINDOW.image(image)

if not run:
    st.warning('Video stopped. Click Activate Camera to start the feed.')

# TODO:
# - Verify the board state makes sense.
# - Send off a web request for states.
# - Render summary graphic and bounds.
# - For now just render the moves suggestion in a separate window.
# - Render the cached moves suggestion image on top of the board.