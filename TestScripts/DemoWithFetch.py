# A demo of GamesPlane that fetches board images online
# python -m streamlit run TestScripts/DemoWithFetch.py

import cv2
import sys
sys.path.append(".")
import asyncio
import numpy as np
import streamlit as st
import threading
import keyboard
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
    print("Camera and Game loaded successfully.")
    ses.turn = "2_"
    ses.cached_corners = {
        12: (0, 0),
        13: (0, 0),
        14: (0, 0),
        15: (0, 0)
    }
    # STATE ESTIMATION
    ses.estimator = MajorityEstimator(max_frames=10)

# 2. ONLINE WINDOW
FRAME_WINDOW = st.image([ ])
st.header("Dao GamesPlane")
run = st.toggle("Activate Camera")

# Display for the number of anchors and pieces spotted.
col_anc, col_piece = st.columns(2)
anc_display = col_anc.empty()
piece_display = col_piece.empty()
anc_display.badge(f"0 anchors", color="red")
piece_display.badge(f"0 pieces", color="blue")
data2 = st.empty()
blacks_turn = st.toggle("Player Turn")
turn_display = st.empty()

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

# Wrapper to run the async function in a thread
def make_loop_for(func, state):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func(state))
    loop.close()

def on_space():
    blacks_turn = not blacks_turn

keyboard.add_hotkey('space', on_space)

# 5. PROCESS VIDEO
while run:
    _, image = ses.camera.read()

    pieces, anchors, reasons = ses.game.process_image(image)
    anc_display.badge(f"{len(anchors)} anchors", color="red")
    piece_display.badge(f"{len(pieces)} pieces", color="blue")

    for info in pieces + anchors:
        #info.put_summary_graphic(image)
        info.put_bounds(image)

    # NOTE: Now try to show the board state.
    # 1. Verify the board state makes sense:
    # - Must find 8 pieces: 4 black, 4 white
    # TODO: Redo to require only one anchor.

    if len(anchors) == 0:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(image)

        #print(f"Error: {len(pieces)=}, {len(anchors)=} \n Needs: (8 pieces, 4 anchors) in frame")
        continue    # IGNORE. Has to find 4 anchors

    # 2. Convert board state to board string
    # - For Dao: X is White, O is Black, - is empty
    # - White turn is 1, Black is 2. Assume 1 for now
    # - TODO: How do we say whose turn it is? Button? 
    
    if len(pieces) == 8:
        board_str = "1_" if not blacks_turn else "2_"
        turn_display.badge("White" if not blacks_turn else "Black", color="gray")
        GRID = len(POS_TO_IDX)
        board_rep = [["-" for c in range(GRID)] for r in range(GRID)]

        for piece in pieces:
            name = "O" if piece.phys.id == 1 else "X"
            pos_x, pos_y = piece.closest_board_position
            idx_x, idx_y = POS_TO_IDX[pos_x][pos_y]
            board_rep[idx_x][idx_y] = name
        
        for y in range(GRID):
            for x in range(GRID):
                board_str += board_rep[x][y]

        # 3. Add board state to state estimator
        ses.estimator.seen_board_state(board_str)
    
    if ses.estimator.has_state():
        best_board = ses.estimator.curr_board_state()    

        data2.badge(best_board)

        corners_to_use = {
            12: "top_r",
            13: "bot_r",
            14: "top_l",
            15: "bot_l"
        }
        for a in anchors:
            ses.cached_corners[a.phys.id] = getattr(a, corners_to_use[a.phys.id]) 

        # This is janky, but it lists the correct way to display the moves image.
        if best_board in st.session_state.fetcher.board_cache:
            correct_order = [
                12, 14, 15, 13
            ]
            
            display_corners = [ses.cached_corners[n] for n in correct_order]

            overlay_image = st.session_state.fetcher.board_cache[best_board]
            image = warp_and_overlay(image, overlay_image, np.array(display_corners))
        else:
            # Start a thread to get this image.
            thread = threading.Thread(target=make_loop_for, args=(ses.fetcher.get_svg_for, best_board))
            thread.start()

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    FRAME_WINDOW.image(image)

if st.button("Write Cache"):
    ses.fetcher.write_cache()

if st.button("Erase Cache"):
    ses.fetcher.erase_cache()