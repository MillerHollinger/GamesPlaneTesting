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
    st.session_state.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
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

# PROCESS VIDEO
# 2. Loop:

state_votes = {}

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
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    FRAME_WINDOW.image(image)
    
    #print(f"Found {len(pieces)} pieces and {len(anchors)} anchors")
    if len(pieces) != 8 or len(anchors) == 0:
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
        name = "X" if piece.phys.id == 1 else "O"
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
    
    most_votes = max(state_votes, key=state_votes.get)
    print(most_votes)
            

        # 2. Send off a web request.
        # 3. Show the current moves suggestion image in a separate window.

        
    # except Exception as e:
    #     print(e)

    

if not run:
    st.warning('Video stopped. Click Activate Camera to start the feed.')


# - Verify the board state makes sense.
# - Send off a web request for this board state.
# - Render summary graphic and bounds.
# - For now: Just render the moves suggestion in a separate window.

# - Render the cached moves suggestion image on top of the board.