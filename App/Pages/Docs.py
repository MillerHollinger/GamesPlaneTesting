# TODO Docs go here.

import streamlit as st

st.set_page_config(page_title="Docs - GamesPlane")
st.header("Docs")

# Topics
# Helper Classes
with st.expander("DigitalAruco"):
    st.markdown("""
    # Class: `DigitalAruco`

    ## Overview
    Represents an ArUco marker detected in a 2D image, enriched with its position, orientation, and physical mapping.

    ## Import
    ```python
    from Helpers/DigitalAruco import DigitalAruco
    ```

    ## Initialization
    ```python
    DigitalAruco(raw_corners, phys: PhysicalAruco, cam_matrix, dist_coeff)
    ```

    ### Parameters
    - `raw_corners` (`List[float]`): Eight pixel coordinate values returned from `aruco.detectMarkers()`.
    - `phys` (`PhysicalAruco`): The corresponding physical ArUco object.
    - `cam_matrix` (`np.ndarray`): The 3x3 camera matrix.
    - `dist_coeff` (`np.ndarray`): The distortion coefficients.

    ## Attributes

    | Attribute | Type | Description |
    |----------|------|-------------|
    | `raw_corners` | `List[float]` | The eight values defining this ArUco's corners in pixel coordinates. |
    | `reshaped_corners` | `List[Tuple[float, float]]` | Four (x, y) coordinates reshaped from `raw_corners`. Ordered as top-left, top-right, bottom-right, bottom-left. |
    | `top_l`, `top_r`, `bot_r`, `bot_l` | `Tuple[float, float]` | Individual (x, y) corners from `reshaped_corners`. |
    | `center` | `Tuple[float, float]` | The marker’s center in image coordinates. |
    | `rvec`, `tvec` | `np.ndarray` | Rotation and translation vectors estimated from the camera’s perspective. |
    | `phys` | `PhysicalAruco` | Reference to the physical marker. |
    | `exact_board_position` | `Tuple[float, float]` | Exact position on the board in board coordinates. |
    | `closest_board_position` | `Tuple[float, float]` | Closest valid position on the board. |

    ## Methods

    ### `to_world_coordinates(cam_matrix, dist_coeff) -> None`
    Uses `aruco.estimatePoseSingleMarkers` to set `rvec` and `tvec`.

    #### Parameters
    - `cam_matrix` (`np.ndarray`): The 3x3 camera matrix.
    - `dist_coeff` (`np.ndarray`): The distortion coefficients.

    ---

    ### `set_board_position(board_position) -> None`
    Sets the board position manually. Only valid for anchored ArUcos.

    #### Parameters
    - `board_position` (`Tuple[float, float]`): The position to assign.

    ---

    ### `fully_defined() -> bool`
    Returns whether all spatial data (`rvec`, `tvec`, `exact_board_position`, and `closest_board_position`) have been calculated.

    ---

    ### `to_board_position(anchor_markers, board, give_reasoning=False) -> Union[Tuple[float, float], Tuple[Tuple[float, float], List[str]]]`
    Estimates the marker’s board position using the known anchor markers.

    #### Parameters
    - `anchor_markers` (`List[DigitalAruco]`): Anchored reference markers.
    - `board` (`PhysicalBoardInfo`): Board metadata.
    - `give_reasoning` (`bool`, optional): If `True`, returns reasoning from each anchor as well.

    ---

    ### `change_basis(rvec1, tvec1, rvec2, tvec2) -> Tuple[np.ndarray, np.ndarray]`
    Transforms a vector pair from one reference frame to another.

    #### Parameters
    - `rvec1`, `tvec1`, `rvec2`, `tvec2` (`np.ndarray`): Rotation and translation vectors.

    ---

    ### `put_summary_graphic(image)`
    Overlays a graphic on the image summarizing the marker's state.

    ---

    ### `put_bounds(image)`
    Draws the detected bounds of the ArUco marker on the input image.

    ---

    ### `string_info() -> str`
    Returns a detailed string representation (alternative to `__str__`) with extended marker information.

    ---
    """)

"""
Class: PhysicalAruco

Overview
A PhysicalAruco represents an actual ArUco marker in the world. 
Anchored ArUcos are ArUcos that are physically attached to on drawn on the game board itself. These are used to find the location of Unanchored ArUcos.  
Unanchored ArUcos are ArUcos that move freely (i.e. game pieces). The position of these pieces is calculated with respect to Anchored ArUcos.

Import
from Helpers/PhysicalAruco import PhysicalAruco

Initialization
PhysicalAruco(id, tag, size, anchored, board_position=None)
id (int) : The ArUco Classic ID associated with this object. 0 to 100.
tag (string) : A tag describing the ArUco. Used to convert the board state to a UWAPI string.
size (float) : In centimeters, the length of one edge of this ArUco. ArUco markers are square, so either edge works.
anchored (bool) : True if anchored. False if unanchored (a game piece).
board_position (Tuple(float, float)) : Leave empty if unanchored. Where this marker is on the board, in (x, y) board coordinates.

Methods
generate_many(ids, tag, size, anchored, board_positions):
A helper function to define many PhysicalAruco objects at once.
It takes in some constants and some lists, and iterates through each, creating objects sequentially using the values at each index.

ids (List[int]) : A list of ids to use for the generated objects.
tag (string) : The tag to use on all generated objects.
size (float) : The size of the ArUcos on one edge.
anchored (bool) : If the generated ArUcos are anchored.
board_positions (List[Tuple(float, float)]) : Where each ArUco is positioned.

"""

"""
Class: PhysicalBoardInfo

Overview
Represents the information associated with a specific game board.

Import
from Helpers/PhysicalBoardInfo import PhysicalBoardInfo

Initialization
PhysicalBoardInfo(unanchored_arucos: list[PhysicalAruco], anchored_arucos: list[PhysicalAruco], valid_board_positions: list[(float, float)], cm_to_space: float = 0):

unanchored_arucos (list[PhysicalAruco]) : A list of unanchored ArUcos (pieces) that will be used in this game. Multiple pieces may share the same ArUco ID.
anchored_arucos (list[PhysicalAruco]) : A list of anchored ArUcos attached to or printed on the board. They may not reuse the same ArUco ID.
valid_board_positions (list[(float, float)]) : A list of positions in board coordinates where pieces may be placed.
cm_to_space (float = 0) : How many centimeters in world space corresponds to one board unit. For example, on a grid board with square spaces 4cm to a side, this would be 4.


Methods
aruco_info_for(id):
Returns the PhysicalAruco object of the first ArUco with the given ID. 

closest_valid_space(board_position)
Given an (x, y) board position, returns the closest valid_board_position.
"""

"""
Class: GamesFrame

Overview
A GamesFrame stores all of the data about a game, including the camera used to view that game. It's the object everything else builds into.

Import
from Helpers/GamesFrame import GamesFrame

Initialization
GamesFrame(camera_yaml: str, board_info: PhysicalBoardInfo):
camera_yaml (str) : The .yaml file path, or loaded yaml data, of the camera's intrinsics.
board_info (PhysicalBoardInfo) : The information about this game's board.

Methods
process_image(image, give_reasoning: bool = False):
Processes an image to find the ArUcos in it, returning DigitalAruco objects.

image (numpy array) : A numpy array from cv2 representing an image to analyze.
give_reasoning (bool) : If it should also return a list of strings expressing the math it did.

returns: Two lists of DigitalAruco objects. The first is the pieces found, the second is the anchors. If give_reasoning is True, returns a third list of string explanations of how its calculations were made.
"""

"""
Class: BoardStateEstimator

Overview
Given the board state estimation at each frame, produces a guess as to what the board actually is in real life. This is a base class that you can build other StateEstimators off of to create more nuanced logic based on time and frequency.

Import
from Helpers/StateEstimator import BoardStateEstimator
from Helpers/StateEstimator import MajorityEstimator
from Helpers/StateEstimator import AgreeingEstimator
from Helpers/StateEstimator import CombinationEstimator

We recommend using MajorityEstimator for most applications.

Initialization
Depends on which StateEstimator you use. For MajorityEstimator:
MajorityEstimator(max_frames=99, max_seconds=None):
max_frames (int) : The number of frames permitted in the sliding window. As new frames are added, if they exceed this window, the oldest frame is deleted.
max_seconds (float) : How long a frame remains "fresh". Frames older than this are deleted.

Methods
seen_board_state(board):
Adds the given board state to the StateEstimator as the most recent state.

board (str) : A UWAPI board string just seen by the camera. This represents a potentially erroneous guess that the StateEstimator will take into account when making its prediction.

curr_board_state()
Returns the StateEstimator's guess for what the board state actually is using its internal logic.

returns (str) : The StateEstimator's UWAPI string guess.

"""