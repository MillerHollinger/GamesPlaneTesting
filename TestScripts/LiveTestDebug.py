"""
Altered version of Josh's Testing_Video.py to work with a live camera.
"""

import cv2
import yaml
import time
from Games.DummyGame import *
import streamlit as st

st.header("Live Feed Debug")

YAML = "CameraCalibration\good_calibration.yaml"

if "camera" not in st.session_state:
    st.session_state.camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    st.session_state.game = DummyGame(YAML)

run = st.checkbox('Activate Camera')
FRAME_WINDOW = st.image([])

st.subheader("Live Results")
datafield = st.text("Waiting for data...")

while run:
    _, image = st.session_state.camera.read()
    try:
        pieces, anchors, reasoning = st.session_state.game.gframe.process_image(image, True)

        datafield.write(f"{len(anchors)} anchors spotted; {len(pieces)} pieces spotted  \n" + "  \n".join(["  \n".join([a for a in r]) for r in reasoning]))

        for info in pieces + anchors:
            info.put_summary_graphic(image)
            info.put_bounds(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(image)
    except Exception as e:
        pass

if not run:
    st.warning('Video stopped. Click Activate Camera to start the feed.')