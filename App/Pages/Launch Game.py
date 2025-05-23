# The launch game page. Shows all games currently available to play, and lets you start their video captures.

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
from App.UwapiConverter import *
from CameraCalibration.auto_calibration import *
from Helpers.StateEstimator import MajorityEstimator

### Add new games below.
#
# Each game is written as:
# <FULL NAME> : {"route": <NAME OF ROUTE ON GAMESMANUNI>, "converter": <UWAPICONVERTER>}
#
# For example, the game Dao is written lowercase in GamesmanUni links, so we add it as:
#   "Dao" : {"route": "dao", "converter": DaoConverter}

NAME_TO_INFO = {
    "Dao" : {"route": "dao", "converter": DaoConverter},
    "Dodgem" : "",
    "Pong Hau K'i" : ""
}


st.set_page_config(page_title="Launch Game - GamesPlane")
st.header("Launch Game")

# 1. CAMERA & GAME
ses = st.session_state

if "chosen_game" not in ses or ses.chosen_game == None:
    ses.chosen_game = st.segmented_control("Choose a game.", (k for k in NAME_TO_INFO.keys()))
    if ses.chosen_game is not None:
        st.rerun()

else:
    if "camera" not in ses:
        ses.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        yaml_str = get_calib_matrices(cam=ses.camera)
        
        ses.game = fetch_game(ses.chosen_game, yaml_str)
        print(ses.chosen_game)
        ses.fetcher = BoardFetcher(NAME_TO_INFO[ses.chosen_game]["route"], "regular")
        print("Camera and Game loaded successfully.")
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
    st.header(f"Playing {ses.chosen_game} with GamesPlane")
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

    def put_text_top_left(image, text, font_scale=1.0, 
                        text_color=(255, 255, 255), 
                        border_color=(0, 0, 0),
                        thickness=2, border_thickness=3, 
                        margin=10):
        """
        Draws text with a border in the top-left corner of the image.

        Parameters:
            image (numpy.ndarray): The OpenCV image.
            text (str): The text to draw.
            font_scale (float): Font size scale.
            text_color (tuple): Text color in BGR.
            border_color (tuple): Outline (border) color in BGR.
            thickness (int): Thickness of the inner text.
            border_thickness (int): Thickness of the border (should be greater than `thickness`).
            margin (int): Margin from the top and left edges.

        Returns:
            numpy.ndarray: Image with outlined text.
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_x = margin
        text_y = margin + text_size[1]

        # Draw border text
        cv2.putText(image, text, (text_x, text_y), font, font_scale, border_color, border_thickness, cv2.LINE_AA)
        # Draw inner text
        cv2.putText(image, text, (text_x, text_y), font, font_scale, text_color, thickness, cv2.LINE_AA)

        return image

    # 5. PROCESS VIDEO
    while run:
        _, image = ses.camera.read()

        pieces, anchors, reasons = ses.game.process_image(image)
        anc_display.badge(f"{len(anchors)} anchors", color="red")
        piece_display.badge(f"{len(pieces)} pieces", color="blue")

        for info in pieces + anchors:
            info.put_bounds(image)

        # 1. Ensure we have at least one anchor. If not, can't calculate positions.
        if len(anchors) == 0:
            # Show whose turn it is on the image.
            image = put_text_top_left(
                image, 
                "Black" if blacks_turn else "White", 
                text_color=(0, 0, 0) if blacks_turn else (255,255,255), 
                border_color=(0, 0, 0) if not blacks_turn else (255,255,255)
            )
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(image)

            continue

        # 2. Convert board state to board string
        # - For Dao: X is White, O is Black, - is empty
        # - White turn is 1, Black is 2. Assume 1 for now
        
        turn_display.badge("White" if not blacks_turn else "Black", color="gray")

        # Use this game's converter to get the board state from the pieces. Do not query if the state is deemed invalid.
        board_str = NAME_TO_INFO[ses.chosen_game]["converter"].convert("Black" if blacks_turn else "White", pieces)
        if board_str == "fail":
            # Show whose turn it is on the image.
            image = put_text_top_left(
                image, 
                "Black" if blacks_turn else "White", 
                text_color=(0, 0, 0) if blacks_turn else (255,255,255), 
                border_color=(0, 0, 0) if not blacks_turn else (255,255,255)
            )
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(image)
            continue

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

        # Show whose turn it is on the image.
        image = put_text_top_left(
            image, 
            "Black" if blacks_turn else "White", 
            text_color=(0, 0, 0) if blacks_turn else (255,255,255), 
            border_color=(0, 0, 0) if not blacks_turn else (255,255,255)
        )

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(image)

    if st.button("Write Cache"):
        ses.fetcher.write_cache()

    if st.button("Erase Cache"):
        ses.fetcher.erase_cache()