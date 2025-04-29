# python -m streamlit run TestScripts/TestLiveStream.py

import cv2
import sys
sys.path.append(".")
import streamlit as st
from Games.DummyGameTTT import *
from CameraCalibration.auto_calibration import *

# CAMERA & GAME
ses = st.session_state
if "camera" not in ses:
    ses.camera = cv2.VideoCapture(0)
    yaml_str = get_calib_matrices(cam=ses.camera)
    ses.game = DummyGame(yaml_str)

# ONLINE WINDOW
FRAME_WINDOW = st.image([ ])
st.header("Live Feed Debug")
st.subheader("Live Results")
run = st.checkbox("Activate Camera")
data = st.text("Waiting for Camera")

# PROCESS VIDEO
while run:
    _, image = ses.camera.read()

    pieces, anchors, reasons = ses.game.process_image(image)
    prefix = f"{len(anchors)} anchors spotted; {len(pieces)} pieces spotted  \n"
    data.write(prefix + "  \n".join(["  \n".join([a for a in r]) for r in reasons]))

    for info in pieces + anchors:
        info.put_summary_graphic(image)
        info.put_bounds(image)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    FRAME_WINDOW.image(image)

if not run:
    st.warning("Video stopped - activate camera.")