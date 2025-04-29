# TODO Docs go here.

import streamlit as st

st.set_page_config(page_title="Docs - GamesPlane")
st.header("Docs")

# Topics
# Helper Classes
"DigitalAruco"
"Represents an ArUco as seen in a 2D image."
"""
.raw_corners : The eight values defining this Aruco's corners in a list. In image pixel coordinates.
.reshaped_corners : raw_corners reshaped into four (x, y) coordinate pairs. In image pixel coordinates. Ordered as top-left, top-right, bottom-right, bottom-left.
.top_r, .bot_r, .bot_l, .top_l : The four corners of .reshaped_corner split into separate (x, y) tuples.
.center : The center of this ArUco in image coordinates.
.rvec, .tvec : The calculated rotation and translation of this ArUco relative to the camera.
.phys : The physical ArUco information corresponding to this DigitalAruco.
.exact_board_position : The exact position of this ArUco in board coordinates (x, y). Anchored ArUcos take on the position of their PhysicalAruco. Unanchored ArUcos have their positions calcuated after calling .to_board_position().
.closest_board_position : The closest valid position of this DigitalAruco on its board.
"""
"""
DigitalAruco(raw_corners, phys: PhysicalAruco, cam_matrix, dist_coeff)
- raw_corners : The eight pixel coordinate values returned from aruco.detectMarkers().
- phys : The corresponding PhysicalAruco object.
- cam_matrix : The 3x3 camera matrix from your camera.
- dist_coeff : The distortion coefficients from your camera.

.to_world_coordinates(cam_matrix, dist_coeff) -> None
Uses aruco.estimatePoseSingleMarkers to set self.rvec and self.tvec.
- cam_matrix : The 3x3 camera matrix from your camera.
- dist_coeff : The distortion coefficients from your camera.

.set_board_position(board_position) -> None
Sets the board position of this ArUco. You may only use this on anchored ArUcos; use to_board_position for unanchored ArUcos.
- board_positon : The position to set.

.fully_defined() -> bool
Returns if .rvec, .tvec, .exact_board_position, and .closest_board_position have been calculated yet.
.to_world_coordinates defines .rvec and .tvec; .to_board_position defines the board positions.

.to_board_position(anchor_markers: List[DigitalAruco], board: PhysicalBoardInfo, give_reasoning: bool = False) -> (x, y) position
Estimates the board position of this DigitalAruco, setting the board position variables of the object and returning the closest valid board position.
- anchor_markers : The DigitalAruco objects of the board's anchors.
- board : The PhysicalBoardInfo object of the board you're playing on.
- give_reasoning : If True, a second return value will be added: a list of strings saying what each anchor estimates as this DigitalAruco's position.

.change_basis(rvec1, tvec1, rvec2, tvec2) -> rvec, tvec
Transforms the basis of the second vec pair to be in the basis of the first vec pair.

.put_summary_graphic(image)
Puts a graphic about this DigitalAruco onto the image that was used to create it.

.put_bounds(image)
Draws the bounds of this DigitalAruco onto the image that was used to create it.

.string_info()
An alternative to the class's __str__ with more info.
"""
# App Classes