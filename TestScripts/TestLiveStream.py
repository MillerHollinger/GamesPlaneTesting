# python -m streamlit run TestScripts/LiveTestDebug.py

import cv2
import sys
sys.path.append(".")
import streamlit as st
from Games.DummyGamePHK import DummyGame
from CameraCalibration.auto_calibration import *

# CAMERA & GAME
if "camera" not in st.session_state:
    st.session_state.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # auto calibration
    _, image = st.session_state.camera.read()
    h, w = image.shape[:2]
    yaml_str = get_calib_matrices(w, h, mode="yaml")
    # yaml string done
    st.session_state.game = DummyGame(yaml_str)

# CAMERA WINDOW
run = st.checkbox("Activate Camera")
FRAME_WINDOW = st.image([])
st.header("Live Feed Debug")
st.subheader("Live Results")
datafield = st.text("Waiting for data...")

# PROCESS VIDEO
while run:
    _, image = st.session_state.camera.read()
    try:
        pieces, anchors, reasoning = st.session_state.game.gframe.process_image(image, True)
        prefix = f"{len(anchors)} anchors spotted; {len(pieces)} pieces spotted  \n"
        datafield.write(prefix + "  \n".join(["  \n".join([a for a in r]) for r in reasoning]))

        for info in pieces + anchors:
            info.put_summary_graphic(image)
            info.put_bounds(image)
    except Exception as e:
        print(f"No viable arucos in frame. {e}")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    FRAME_WINDOW.image(image)

if not run:
    st.warning('Video stopped. Click Activate Camera to start the feed.')