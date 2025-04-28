# A demo of GamesPlane that fetches board images off the net.

import cv2
import sys
sys.path.append(".")
import streamlit as st
from App.ConvertJSON import fetch_game
from CameraCalibration.auto_calibration import *
from App.BoardFetcher import BoardFetcher
import asyncio

# 1. Setup.
if "camera" not in st.session_state:
    st.session_state.camera = cv2.VideoCapture(0)
    st.session_state.game = fetch_game("Dao")
    st.session_state.fetcher = BoardFetcher("Dao", "regular")

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

# PROCESS VIDEO
# 2. Loop:
while run:
    # Get image.
    _, image = st.session_state.camera.read()
    try:
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
        # - Must find 4 anchors. (for now)
        # 2. Convert to board state.
        # - For Dao, X is White and O is Black. Empty spaces are -. White's turn is 1, black's is 2.
        # - PROBLEM: How do we say whose turn it is? A button? 
        # 2. Send off a web request.
        # 3. Show the current moves suggestion image in a separate window.

    except Exception:
        print("No viable arucos in frame.")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    FRAME_WINDOW.image(image)

if not run:
    st.warning('Video stopped. Click Activate Camera to start the feed.')


# - Verify the board state makes sense.
# - Send off a web request for this board state.
# - Render summary graphic and bounds.
# - For now: Just render the moves suggestion in a separate window.

# - Render the cached moves suggestion image on top of the board.