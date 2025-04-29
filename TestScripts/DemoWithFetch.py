# A demo of GamesPlane that fetches board images off the net.

import cv2
import sys
sys.path.append(".")
import streamlit as st
from App.ConvertJSON import fetch_game
from CameraCalibration.auto_calibration import *
from App.BoardFetcher import BoardFetcher
import asyncio
import numpy as np

# 1. Setup.
if "camera" not in st.session_state:
    st.session_state.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    st.session_state.game = fetch_game("Dao")
    st.session_state.fetcher = BoardFetcher("dao", "regular")

    print("Camera and game are set up.")

# CAMERA WINDOW
run = st.checkbox("Activate Camera")
FRAME_WINDOW = st.image([])
st.header("Live Feed Debug")
st.subheader("Live Results")
datafield = st.text("Waiting for data...")

async def make_request(board_state):
    asyncio.create_task(st.session_state.fetcher.get_svg_for("1_-----BW--WB-----"))

    pass

# x, y
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

# PROCESS VIDEO
# 2. Loop:

state_votes = {}
total_votes = 0
MIN_VOTES_TO_RENDER = 20 # You need this many votes before web requests will be sent out.

while run:
    # Get image.
    _, image = st.session_state.camera.read()
    # try:
    # Process image.
    pieces, anchors, reasoning = st.session_state.game.gframe.process_image(image, True)
    prefix = f"{len(anchors)} anchors spotted; {len(pieces)} pieces spotted  \n"
    datafield.write(prefix + "  \n".join(["  \n".join([a for a in r]) for r in reasoning]))

    # Show basic aruco info.
    for info in pieces + anchors:
        info.put_summary_graphic(image)
        info.put_bounds(image)

    x = 0
    # Now, try to show the board state as well.
    # 1. Verify the board state makes sense:
    # - Must find 8 pieces, 4 black and 4 white.
    
    #print(f"Found {len(pieces)} pieces and {len(anchors)} anchors")
    if len(pieces) != 8 or len(anchors) != 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(image)
        #print("Can't see all 8 pieces and at least one anchor.")
        continue
    # ignoring - Must find 4 anchors. (for now)

    # 2. Convert to board state.
    # - For Dao, X is White and O is Black. Empty spaces are -. White's turn is 1, black's is 2.
    # - PROBLEM: How do we say whose turn it is? A button? 
    # For now assume it's white's turn.
    board_string = "1_"
    board_rep = [["-" for i in range(4)] for k in range(4)]
    for piece in pieces:
        name = "O" if piece.phys.id == 1 else "X"
        #print(piece.closest_board_position)
        board_pos = POS_TO_IDX[piece.closest_board_position[0]][piece.closest_board_position[1]]
        board_rep[board_pos[0]][board_pos[1]] = name
    
    for y in range(4):
        for x in range(4):
            board_string += board_rep[x][y]

    # Add the vote to the current board state estimate.
    if board_string in state_votes:
        state_votes[board_string] += 1
    else:
        state_votes[board_string] = 1
    total_votes += 1

    # Wipe votes every 150 for up-to-date info.
    if total_votes >= 150:
        #print("Resetting votes.")
        total_votes = 0
        state_votes = {}
    
    if total_votes >= MIN_VOTES_TO_RENDER:
        most_votes = max(state_votes, key=state_votes.get)
        print(most_votes)
        # 2. Send off a web request.
        #print("Going to try to fetch a png.")
        asyncio.run(st.session_state.fetcher.get_svg_for(most_votes))

        correct_order = {
            12: 1,
            13: 4,
            14: 2,
            15: 3
        }
        
        if most_votes in st.session_state.fetcher.board_cache:
            print("Got an overlay.")
            #image = overlay_image(image, st.session_state.fetcher.board_cache[most_votes], 0, 0)
            white_square = np.full((100, 100, 4), 255, dtype=np.uint8)

            # TODO Get correct positions to display over.
            display_corners = [a.center for a in sorted(anchors, key=lambda a: correct_order[a.phys.id])]

            image = warp_and_overlay(image, white_square, np.array(display_corners))
            #image = warp_and_overlay(image, st.session_state.fetcher.board_cache[most_votes], np.array(((0, 0), (100, 0), (100, 100), (0, 100))))
            print(image.shape)
        # 3. Show the current moves suggestion image on top.
        else:
            pass
            #print("Not ready to show an image yet.")

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(image)

        
    # except Exception as e:
    #     print(e)

    

if not run:
    st.warning('Video stopped. Click Activate Camera to start the feed.')


# - Verify the board state makes sense.
# - Send off a web request for this board state.
# - Render summary graphic and bounds.
# - For now: Just render the moves suggestion in a separate window.

# - Render the cached moves suggestion image on top of the board.