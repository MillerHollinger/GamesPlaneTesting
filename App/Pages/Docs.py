# TODO Docs go here.

import streamlit as st

st.set_page_config(page_title="Docs - GamesPlane")
st.header("Docs")

with st.expander("Adding a New Game"):
    st.markdown("""
    Adding a new game to GamesPlane has these steps, which will be explained in more detail below:

    1. Create a physical board and pieces
    2. Create the .json file in Craftsman
    3. Write a UWAPI converter
    4. Register the game in `Launch Game.py`

    #### Step 1: Create a Physical Board and Pieces
    You'll need to create a board for your game with ArUco anchors, and then make ArUco pieces.
    You can start with [this template](https://docs.google.com/presentation/d/1WUdp0DYTSKhTM55Ek5bQRoZIVrDISUIf8kJTF1hCyMw/edit?usp=sharing).
    1. Make your board.
        - You must have at least one anchor printed on the board.
        - Each anchor should be a different ArUco ID.
    2. Make your pieces.
        - Several pieces may share the same ArUco. It is common to do with with equivalent pieces: e.g. for checkers, all the black checkers could be ArUco ID 1 and all the white ones could be ID 2.
    3. Print out your board and pieces.  

    You can click on an object and go Format options > Position to see its exact position. We often use From: Center in this panel to make the coordinate values smaller and easier to work with.

    #### Step 2: Create the .json File in Craftsman
    Go to the Craftsman tab in GamesPlane.
    1. Add your **game's name**.
    2. Set your **Centimeters to Space**. We usually use inches as space units, so type 2.54 unless you have a plan.
    3. For each anchor, click **Add New ArUco**.
        - Its tag can be anything. We usually use anchor_ID where ID is the ID you will assign it.
        - ArUco ID is the ID of the specific anchor ArUco you are adding. Check the last page of the template for a key.
        - Size is the length of a black edge of the ArUco. You can use Format options to see the element's size in Google Slides.
        - Check "Anchored."
        - Set its position X and position Y to the values in Format options, i.e. its position in inches.
        - Click Add ArUco. Repeat for each anchor (4 anchors if you use the template)
    4. For each piece type, click **Add New ArUco**.
        - Its tag should be a short name for how you refer to that piece. "black" and "white" are common choices.
        - ArUco ID is the ID of the specific piece ArUco you are adding. Check the last page of the template for a key.
        - Size is the length of a black edge of the ArUco. You can use Format options to see the element's size in Google Slides.
        - Click Add ArUco. Do not click Anchored.
    5. Add the valid board positions. If you added spaces, you can again use Format Options to see the coordinates of each space you added.
    6. (Optional) Upload the PDF of your game.  You can also share it through other means.
    7. Click "Save". The data you input will be saved to a .json file. You can edit that file if you change your mind on anything instead of retyping everything into Craftsman.

    #### Step 3: Write a UWAPI Converter
    You need to provide logic to convert a list of DigitalAruco objects to a UWAPI string. 
    1. Check the GamesmanUni of the game you are adding to understand how it forms UWAPI strings for that game. 
    2. Go to `App/UwapiConverter.py`. Create a class extending UwapiConverter; you can use DaoConverter as an example.
    3. Give it the function `convert`. Again, see DaoConverter to see how this looks. It takes in the current turn and a list of DigitalAruco objects.
    4. Write logic that uses the DigitalAruco objects (likely using their `.closest_board_position` property and `.tag` property) to make a UWAPI string.
        - Not all board states are valid: You can return `"fail"` if the provided state should not be sent to GamesmanUni. 

    #### Step 4: Register the game in `Launch Game.py`
    Now it's time to make `Launch Game.py` aware of your new game, which will add it as an option to play.
    1. Find the dictionary `NAME_TO_INFO` near the top of the file.
    2. Add your game to the dictionary in this format (you may use Dao as a reference again): 
        - `"Name" : {"route" : "the name of this game's route on GamesmanUni", "converter" : YourGamesConverter}`
        - `"route"` forms part of the GamesmanUni URL. Here are some examples:
            - https://nyc.cs.berkeley.edu/uni/games/foxandhounds/variants/regular -> "foxandhounds"
            - https://nyc.cs.berkeley.edu/uni/games/fourfieldkono/variants/standard -> "fourfieldkono"
            - https://nyc.cs.berkeley.edu/uni/games/mutorere/variants/regular -> "mutorere"
        - `"converter"` maps to your converter class. It is not a string.

    #### Play!
    Your game should now be added! Restart Streamlit if necessary and click your game's name in the list to play.

    """)

# Topics
# Helper Classes
with st.expander("DigitalAruco"):
    st.markdown("""
    # Class: `DigitalAruco`

    ## Overview
    Represents an ArUco marker detected in a 2D image, enriched with its position, orientation, and physical mapping.

    ## Import
    ```python
    from Helpers.DigitalAruco import DigitalAruco
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

with st.expander("PhysicalAruco"):
    st.markdown("""
    # Class: `PhysicalAruco`

    ## Overview
    A `PhysicalAruco` represents an actual ArUco marker in the world.

    Anchored ArUcos are physically attached to or drawn on the game board. These are used to determine the location of unanchored ArUcos.  
    Unanchored ArUcos move freely (e.g., game pieces), and their position is calculated relative to anchored ArUcos.

    ## Import
    ```python
    from Helpers.PhysicalAruco import PhysicalAruco
    ```

    ## Initialization

    ```python
    PhysicalAruco(id, tag, size, anchored, board_position=None)
    ```

    ### Parameters

    * `id` (`int`): The ArUco Classic ID associated with this object. Ranges from 0 to 100.
    * `tag` (`str`): A tag describing the ArUco. Used to convert the board state to a UWAPI string.
    * `size` (`float`): The length (in cm) of one edge of this square marker.
    * `anchored` (`bool`): `True` if the marker is anchored to the board, `False` if it's a movable piece.
    * `board_position` (`Tuple[float, float]`, optional): Board coordinates of the marker. Leave empty if unanchored.

    ## Methods

    ### `generate_many(ids, tag, size, anchored, board_positions) -> List[PhysicalAruco]`

    A helper function to define multiple `PhysicalAruco` objects at once. It uses constant values and iterates over lists to construct each object sequentially.

    #### Parameters

    * `ids` (`List[int]`): A list of IDs for the generated markers.
    * `tag` (`str`): The tag to assign to all generated markers.
    * `size` (`float`): The size of each marker (edge length).
    * `anchored` (`bool`): Whether the generated markers are anchored.
    * `board_positions` (`List[Tuple[float, float]]`): List of positions for each generated marker.

    """)

with st.expander("PhysicalBoardInfo"):
    st.markdown("""
    # Class: `PhysicalBoardInfo`

    ## Overview
    Represents the information associated with a specific game board.

    ## Import
    ```python
    from Helpers.PhysicalBoardInfo import PhysicalBoardInfo
    ```

    ## Initialization

    ```python
    PhysicalBoardInfo(unanchored_arucos, anchored_arucos, valid_board_positions, cm_to_space=0)
    ```

    ### Parameters

    * `unanchored_arucos` (`List[PhysicalAruco]`): A list of unanchored ArUcos (movable pieces) used in the game. Multiple pieces may share the same ArUco ID.
    * `anchored_arucos` (`List[PhysicalAruco]`): A list of anchored ArUcos physically attached to or printed on the board. These must use unique ArUco IDs.
    * `valid_board_positions` (`List[Tuple[float, float]]`): List of valid positions (in board coordinates) where pieces can be placed.
    * `cm_to_space` (`float`, optional): Conversion factor from centimeters to board units. For example, if one grid space is 4 cm, this should be `4`.

    ## Methods

    ### `aruco_info_for(id) -> PhysicalAruco`

    Returns the `PhysicalAruco` object corresponding to the first ArUco with the given ID.

    #### Parameters

    * `id` (`int`): The ArUco ID to look up.

    ---

    ### `closest_valid_space(board_position) -> Tuple[float, float]`

    Given a board position, returns the closest valid position from `valid_board_positions`.

    #### Parameters

    * `board_position` (`Tuple[float, float]`): The closest valid board position.

    """)

with st.expander("GamesFrame"):
    st.markdown("""
    # Class: `GamesFrame`

    ## Overview
    A `GamesFrame` stores all the data about a game, including the camera used to view that game. It's the central object that everything else builds into.

    ## Import
    ```python
    from Helpers.GamesFrame import GamesFrame
    ```

    ## Initialization

    ```python
    GamesFrame(camera_yaml, board_info)
    ```

    ### Parameters

    * `camera_yaml` (`str`): The `.yaml` file path or preloaded YAML data containing the camera’s intrinsic parameters.
    * `board_info` (`PhysicalBoardInfo`): Information about the game’s board, including ArUco markers and valid positions.

    ## Methods

    ### `process_image(image, give_reasoning=False) -> Union[Tuple[List[DigitalAruco], List[DigitalAruco]], Tuple[List[DigitalAruco], List[DigitalAruco], List[str]]]`

    Processes an image to detect ArUco markers and returns corresponding `DigitalAruco` objects.

    #### Parameters

    * `image` (`np.ndarray`): A NumPy array representing the image to analyze (from `cv2`).
    * `give_reasoning` (`bool`, optional): If `True`, also returns a list of string explanations of the math used to arrive at the given conclusion.

    #### Returns

    * `List[DigitalAruco]`: The detected unanchored pieces.
    * `List[DigitalAruco]`: The detected anchor markers.
    * `List[str]` (optional): Explanations of the spatial calculations, if `give_reasoning=True`.
    """)

with st.expander("BoardStateEstimator"):
    st.markdown("""
    # Class: `BoardStateEstimator`

    ## Overview
    Given the estimated board state at each frame, this class produces a guess of the actual, real-life board state.

    This is a **base class** used to build more advanced estimators that incorporate time-based or frequency-based logic.  
    We recommend using `MajorityEstimator` for most applications.

    ## Import
    ```python
    from Helpers.StateEstimator import BoardStateEstimator
    from Helpers.StateEstimator import MajorityEstimator
    from Helpers.StateEstimator import AgreeingEstimator
    from Helpers.StateEstimator import CombinationEstimator
    ```

    ## Initialization

    Initialization depends on which `StateEstimator` subclass you use.
    For `MajorityEstimator`:

    ```python
    MajorityEstimator(max_frames=99, max_seconds=None)
    ```

    ### Parameters

    * `max_frames` (`int`, optional): Maximum number of frames to retain in the sliding window. When exceeded, the oldest frame is discarded.
    * `max_seconds` (`float`, optional): Time in seconds a frame remains "fresh". Older frames are removed automatically.

    ## Methods

    ### `seen_board_state(board) -> None`

    Adds the given board state to the estimator as the most recent observation.

    #### Parameters

    * `board` (`str`): A UWAPI board string created by the camera's observation. Represents a possibly erroneous snapshot to be included in estimation.

    ---

    ### `curr_board_state() -> str`

    Returns the estimator’s current guess of the true board state, based on its internal logic and history.

    #### Returns

    * `str`: A UWAPI string representing the estimator's current best guess.
    """)