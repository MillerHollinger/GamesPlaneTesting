import cv2
import sys
sys.path.append(".")
import streamlit as st
from Games.DummyGameTTT import *
from CameraCalibration.auto_calibration import *

YAML = "CameraCalibration/good_calibration.yaml"

st.header("Live Feed Debug")

if "camera" not in st.session_state:
    st.session_state.camera = cv2.VideoCapture(0)

    # auto calibration
    _, image = st.session_state.camera.read()
    h, w = image.shape[:2]
    yaml_str = get_calib_matrices(w, h, mode="yaml")

    st.session_state.game = DummyGame(yaml_str)

run = st.checkbox('Activate Camera')
FRAME_WINDOW = st.image([])

st.subheader("Live Results")
datafield = st.text("Waiting for data...")

while run:
    _, image = st.session_state.camera.read()
    try:
        pieces, anchors, reasoning = st.session_state.game.gframe.process_image(image, True)
        prefix = f"{len(anchors)} anchors spotted; {len(pieces)} pieces spotted  \n"
        datafield.write(prefix + "  \n".join(["  \n".join([a for a in r]) for r in reasoning]))

        for info in pieces + anchors:
            info.put_summary_graphic(image)
            info.put_bounds(image)
    except Exception:
        print("No viable arucos in frame.")
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    FRAME_WINDOW.image(image)

if not run:
    st.warning('Video stopped. Click Activate Camera to start the feed.')