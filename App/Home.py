import streamlit as st
from App.ConvertJSON import fetch_game, write_game
from Helpers.PhysicalAruco import PhysicalAruco
from Games.GamesPlaneGame import GamesPlaneGame

# TODO Ensure everything in this is saved as session data so you can come back later.

# Title
st.set_page_config(page_title="Welcome to GamesPlane")

# JSON Display
#obj = fetch_game("Dummy Game")

if "anchored" not in st.session_state:
    st.session_state.anchored = []
    st.session_state.unanchored = []
    pass

def make_editor(phys_aruco):
    return lambda: define_aruco(phys_aruco)

@st.dialog("Define an ArUco")
# TODO Make the editing work.
def define_aruco(phys_aruco = None):
    if phys_aruco == None:
        st.write("Specify information about a new ArUco marker.")
    else:
        st.write("Edit an ArUco marker.")
    tag = st.text_input("Tag", help="A tag to refer to this ArUco by.  \nExample: A chess rook would be tagged 'rook'.'")
    id = st.number_input("ArUco ID", min_value=0, max_value=100, help="This ArUco's ID. Only use Original ArUco markers.")
    size = st.number_input("Size (cm)", help="The size of one of this ArUco's edges in centimeters.")
    anchored = st.checkbox("Anchored", help="If this ArUco is anchored.  \nCheck if this ArUco is attached to the board. Uncheck if it's on a game piece.")
    if anchored:
        col1, col2 = st.columns(2)
        pos_x = col1.number_input("Position X", help="Horizontal position in board units. Rightwards is positive.")
        pos_y = col2.number_input("Position Y", help="Vertical position in board units. Upwards is positive.")

    if st.button("Save ArUco"):
        if tag == "":
            st.error("Please enter a tag for this ArUco.")
        else:
            (st.session_state.anchored if anchored else st.session_state.unanchored).append(PhysicalAruco(
                int(id),
                tag,
                float(size),
                anchored,
                [pos_x, pos_y] if anchored else None
            ))
            st.rerun()

st.header("Game Editor")
top1, top2 = st.columns(2)
name = top1.text_input("Game Name", help="The name of your game. This will be used to save the game, so do not use the same name as another game.")
cm_to_space = top2.number_input("Centimeters to Space", help="How many cm equates to one board space unit.  \nFor example, on a checkboard with 5cm wide spaces, you'd put 5cm.")

aru_c = st.container(border=True)

def show_aruco(phys_aruco):
    c = aru_c.container(border=True)
    col1, col2, col3, col4, col5, col6 = c.columns(6)
    col1.badge("Anchored" if phys_aruco.anchored else "Unanchored", color="red" if phys_aruco.anchored else "blue")
    col2.write(phys_aruco.tag)
    col3.write(f"ID {phys_aruco.id}")
    col4.write(f"{phys_aruco.size} cm")
    col5.write(f"at ({phys_aruco.board_position[0]}, {phys_aruco.board_position[1]})" if phys_aruco.anchored else "")
    
    # TODO Make these buttons work
    b1, b2 = col6.columns(2)
    b1.button("✏️", key=f"{phys_aruco.tag} {phys_aruco.anchored} {phys_aruco.board_position} edit", on_click=make_editor(phys_aruco))
    b2.button("🗑️", key=f"{phys_aruco.tag} {phys_aruco.anchored} {phys_aruco.board_position} trash")

aru_c.subheader("Anchored ArUcos", divider="red")

if len(st.session_state.anchored) > 0:
    for aru in st.session_state.anchored:
        show_aruco(aru)
else:
    aru_c.caption("No Anchored ArUcos added yet. Add some with the Add New ArUco button!")

aru_c.subheader("Unanchored ArUcos", divider="blue")

if len(st.session_state.unanchored) > 0:
    for aru in st.session_state.unanchored:
        show_aruco(aru)
else:
    aru_c.caption("No Unanchored ArUcos added yet. Add some with the Add New ArUco button!")

if aru_c.button("Add New ArUco"):
    define_aruco(aru_c)

def get_errors_and_warnings():
    errors = []
    warnings = []

    if name == "":
        errors.append("Add a name to the game.")

    if cm_to_space == 0:
        errors.append("Enter a nonzero value for centimeters per board space.")
    elif cm_to_space < 4:
        warnings.append("Your centimeters per space is low. Consider at least 4cm per space.")

    if len(st.session_state.anchored) == 0:
        errors.append("Define at least one Anchored ArUco.")
    elif len(st.session_state.anchored) < 2:
        warnings.append("Try to have at least 2 anchors for better accuracy.")
    
    if len(st.session_state.unanchored) == 0:
        warnings.append("No unanchored ArUcos (pieces) are defined.")
    
    return errors, warnings


errors, warnings = get_errors_and_warnings()
if len(errors) > 0 or len(warnings) > 0:
    for r in errors:
        st.error(r)
    for r in warnings:
        st.warning(r)
else:
    st.success("Ready to save!")

save = st.button("Save", disabled=len(errors) != 0, type="primary")

pos_c = st.container()

if save:
    gpg = GamesPlaneGame(name, st.session_state.anchored, st.session_state.unanchored,
                         [(0, 0)], cm_to_space, r"Camera Calibration\good_calibration.yaml")

    path = write_game(gpg)
    st.write(f"Saved game to {path}!")
