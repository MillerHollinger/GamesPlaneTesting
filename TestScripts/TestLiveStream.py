# python -m streamlit run TestScripts/TestLiveStream.py

import cv2
import sys
sys.path.append(".")
import asyncio
import numpy as np
import streamlit as st
from Games.DummyGamePHK import DummyGame
from CameraCalibration.auto_calibration import *
from Helpers.StateEstimator import MajorityEstimator

ses = st.session_state

# CAMERA & GAME
if "camera" not in ses:
    ses.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # auto calibration
    _, image = ses.camera.read()
    h, w = image.shape[:2]
    yaml_str = get_calib_matrices(w, h, mode="yaml")
    # yaml string done
    ses.game = DummyGame(yaml_str)

# ONLINE WINDOW
FRAME_WINDOW = st.image([ ])
st.header("Live Feed Debug")
st.subheader("Live Results")
run = st.checkbox("Activate Camera")
data = st.text("Waiting for Camera")
data2 = st.text("")

# STATE ESTIMATION
estimator = MajorityEstimator()
GRID = 4

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

    if not anchors or not pieces:
        continue

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
    
    # if len(estimator.queue) > MIN_FRAMES:
    pred_state = estimator.curr_board_state()
    data2.write("Estimated board state: " + pred_state)

if not run:
    st.warning("Video stopped - activate camera.")