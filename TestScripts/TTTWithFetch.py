# python -m streamlit run TestScripts/TTTWithFetch.py

import cv2
import sys
sys.path.append(".")
import asyncio
import numpy as np
import streamlit as st
from Games.DummyGameTTT import *
# from App.ConvertJSON import fetch_game
# from App.BoardFetcher import BoardFetcher
from CameraCalibration.auto_calibration import *
from Helpers.StateEstimator import MajorityEstimator

# CAMERA & GAME
ses = st.session_state
if "camera" not in ses:
    ses.camera = cv2.VideoCapture(0)
    yaml_str = get_calib_matrices(cam=ses.camera)
    ses.game = DummyGame(yaml_str)

    # TODO: re-enable
    # ses.game = fetch_game("Dao")
    # ses.fetcher = BoardFetcher("dao", "regular")

# ONLINE WINDOW
FRAME_WINDOW = st.image([ ])
st.header("Live Feed Debug")
st.subheader("Live Results")
run = st.checkbox("Activate Camera")
data = st.text("Waiting for Camera")
data2 = st.text("")

# TODO: re-enable
# async def make_request(board_state):
#     asyncio.create_task(ses.fetcher.get_svg_for("1_-----BW--WB-----"))

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

# PROCESS VIDEO
while run:
    _, image = ses.camera.read()

    pieces, anchors, reasons = ses.game.process_image(image)
    prefix = f"{len(anchors)} anchors spotted; {len(pieces)} pieces spotted  \n"
    data.write(prefix)# + "  \n".join(["  \n".join([a for a in r]) for r in reasons]))

    for info in pieces + anchors:
        info.put_summary_graphic(image)
        info.put_bounds(image)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    FRAME_WINDOW.image(image)

    if not anchors:# or not pieces:
        continue

    # TODO:
    # Abstract board verification logic away using
    # something like ses.game.verify_board_state()

    # Convert to board string. Assume X's/1's turn
    board_str = "1_"
    board_rep = [["-" for c in range(GRID)] for r in range(GRID)]
    
    for piece in pieces:
        name = piece.phys.tag
        x, y = piece.closest_board_position
        board_rep[x][y] = name
    
    for r in range(GRID):
        for c in range(GRID):
            board_str += board_rep[c][r]

    # Add board string to state estimator
    estimator.seen_board_state(board_str)
    MIN_FRAMES = 20
    
    if len(estimator.queue) > MIN_FRAMES:
        pred_state = estimator.curr_board_state()
        
        # TODO: re-enable
        # asyncio.run(ses.fetcher.get_svg_for(pred_state))
        # cache = ses.fetcher.board_cache
        # if pred_state in cache:
        #     image = overlay_image(image, cache[pred_state], 0, 0)

        data2.write("Estimated board state: " + pred_state)

if not run:
    st.warning("Video stopped - activate camera.")