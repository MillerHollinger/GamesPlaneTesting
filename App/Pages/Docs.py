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
    from your_module import DigitalAruco
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