import streamlit as st
from App.ConvertJSON import fetch_game, write_game
from Helpers.PhysicalAruco import PhysicalAruco
from Games.GamesPlaneGame import GamesPlaneGame

# This file uses Streamlit to build the UI.
# Streamlit docs: https://docs.streamlit.io/

# TODO Load data from a json to edit.

# Title and Header
st.set_page_config(page_title="Craftsman - GamesPlane")
st.header("Craftsman", help="Craftsman is GamesPlane's tool for defining new games.  \nSet up your game's ArUco and board information here!")

st.subheader("Set Up a Game")
# JSON Display
#obj = fetch_game("Dummy Game")

if "arucos" not in st.session_state:
    st.session_state.arucos = []
    st.session_state.positions = []
    pass

# Helper function. Edit buttons call this.
def make_editor(phys_aruco):
    return lambda: define_aruco(phys_aruco)

# Defines an ArUco.
# If an ArUco argument is provided, it edits that ArUco instead.
@st.dialog("Define an ArUco")
def define_aruco(phys_aruco = None):
    if phys_aruco == None:
        st.write("Specify information about a new ArUco marker.")
    else:
        st.write("Edit an ArUco marker.")
    
    default_tag = "" if phys_aruco is None else phys_aruco.tag
    default_id = 0 if phys_aruco is None else phys_aruco.id
    default_size = 0.0 if phys_aruco is None else phys_aruco.size
    default_anchored = False if phys_aruco is None else phys_aruco.anchored
    default_posX = 0.0 if phys_aruco is None or not phys_aruco.anchored else phys_aruco.board_position[0]
    default_posY = 0.0 if phys_aruco is None or not phys_aruco.anchored else phys_aruco.board_position[1]

    tag = st.text_input("Tag", help="A tag to refer to this ArUco by.  \nExample: A chess rook would be tagged 'rook'.'", value=default_tag)
    id = st.number_input("ArUco ID", min_value=0, max_value=100, help="This ArUco's ID. Only use Original ArUco markers.", value=default_id)
    size = st.number_input("Size (cm)", help="The size of one of this ArUco's edges in centimeters.", value=default_size)
    anchored = st.checkbox("Anchored", help="If this ArUco is anchored.  \nCheck if this ArUco is attached to the board. Uncheck if it's on a game piece.", value=default_anchored)
    if anchored:
        
        col1, col2 = st.columns(2)
        pos_x = col1.number_input("Position X", help="Horizontal position in board units. Rightwards is positive.", value=default_posX)
        pos_y = col2.number_input("Position Y", help="Vertical position in board units. Upwards is positive.", value=default_posY)

    finish_name = "Add ArUco" if phys_aruco is None else "Update ArUco"
    if st.button(finish_name):
        if tag == "":
            st.error("Please enter a tag for this ArUco.")
        else:
            if phys_aruco is None:        
                st.session_state.arucos.append(PhysicalAruco(
                    int(id),
                    tag,
                    float(size),
                    anchored,
                    [pos_x, pos_y] if anchored else None
                ))
            else:
                phys_aruco.id = int(id)
                phys_aruco.tag = tag
                phys_aruco.size = float(size)
                phys_aruco.anchored = anchored
                phys_aruco.board_position = [pos_x, pos_y] if anchored else None
            st.rerun()

# Top section of page: Name and CM to space
top1, top2 = st.columns(2)
st.session_state.name = top1.text_input("Game Name", help="The name of your game. This will be used to save the game, so do not use the same name as another game.")
st.session_state.cm_to_space = top2.number_input("Centimeters to Space", help="How many cm equates to one board space unit.  \nFor example, on a checkboard with 5cm wide spaces, you'd put 5cm.", min_value=0.0)

# ArUco display container
aru_c = st.container(border=True)

# Shows an aruco's information as a bar
def show_aruco(phys_aruco):
    c = aru_c.container(border=True)
    col1, col2, col3, col4, col5, col6 = c.columns(6)
    col1.badge("Anchored" if phys_aruco.anchored else "Unanchored", color="red" if phys_aruco.anchored else "blue")
    col2.write(phys_aruco.tag)
    col3.write(f"ID {phys_aruco.id}")
    col4.write(f"{phys_aruco.size} cm")
    col5.write(f"at ({phys_aruco.board_position[0]}, {phys_aruco.board_position[1]})" if phys_aruco.anchored else "")
    
    b1, b2 = col6.columns(2)
    b1.button("✏️", key=f"{phys_aruco.tag} {phys_aruco.anchored} {phys_aruco.board_position} edit", on_click=make_editor(phys_aruco))
    # TODO Trash button
    b2.button("🗑️", key=f"{phys_aruco.tag} {phys_aruco.anchored} {phys_aruco.board_position} trash")

# Show anchored arucos
aru_c.subheader("Anchored ArUcos", divider="red")

def split_anchored():
    anchored = []
    unanchored = []
    for aru in st.session_state.arucos:
        if aru.anchored:
            anchored.append(aru)
        else:
            unanchored.append(aru)
    return anchored, unanchored

anchored, unanchored = split_anchored()

if len(anchored) > 0:
    for aru in anchored:
        show_aruco(aru)
else:
    aru_c.caption("No Anchored ArUcos added yet. Add some with the Add New ArUco button!")

# Show unanchored arucos
aru_c.subheader("Unanchored ArUcos", divider="blue")

if len(unanchored) > 0:
    for aru in unanchored:
        show_aruco(aru)
else:
    aru_c.caption("No Unanchored ArUcos added yet. Add some with the Add New ArUco button!")

# Button to add a new aruco
if aru_c.button("Add New ArUco"):
    define_aruco()

# Add board positions.
pos_c = st.container(border=True)
pos_c.subheader("Board Positions", divider="grey")

def pos_index_deleter(index):
    return lambda: st.session_state.positions.pop(index)

def show_board_pos(pos, index):
    c = pos_c.container(border=True)
    c1, c2 = c.columns(2)
    c1.text(f"({pos[0]}, {pos[1]})")
    c2.button("🗑️", key=f"{index} trash", on_click=pos_index_deleter(index))

for i in range(len(st.session_state.positions)):
    show_board_pos(st.session_state.positions[i], i)

@st.dialog("Add a Board Position")
def add_board_pos():
    col1, col2 = st.columns(2)
    pos_x = col1.number_input("Position X", key="add_pos_x", help="Horizontal position in board units. Rightwards is positive.", value=0.0)
    pos_y = col2.number_input("Position Y", key="add_pos_y", help="Vertical position in board units. Upwards is positive.", value=0.0)
    if st.button("Add Board Position", key="add_pos"):
        st.session_state.positions.append((pos_x, pos_y))
        st.rerun()

if pos_c.button("Add Board Position"):
    add_board_pos()

# TODO Add board PDF.
uploaded_file = st.file_uploader("Game Board PDF (optional)", type="pdf", help="The PDF of your game's board. Your PDF will be saved for easy retrieval.")

def save_uploaded_pdf(uploaded_file, save_path):
    with open(save_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

# Get and show the current issues with data entered so far
def get_errors_and_warnings():
    errors = []
    warnings = []

    if st.session_state.name == "":
        errors.append("✏️ Set a name for the game.")

    if st.session_state.cm_to_space == 0:
        errors.append("📏 Enter a nonzero value for centimeters per board space.")
    elif st.session_state.cm_to_space < 4:
        warnings.append("📏 Your centimeters per space is low. Consider at least 4cm per space.")

    if len(anchored) == 0:
        errors.append("⚓️ Define at least one Anchored ArUco.")
    elif len(anchored) < 2:
        warnings.append("⚓️ Try to have at least 2 anchors for better accuracy.")
    
    if len(unanchored) == 0:
        warnings.append("♟️ No unanchored ArUcos (pieces) are defined.")

    if len(st.session_state.positions) == 0:
        errors.append("🗺️ Define at least one board position.")
    
    return errors, warnings

errors, warnings = get_errors_and_warnings()
if len(errors) > 0 or len(warnings) > 0:
    for r in errors:
        st.error(r)
    for r in warnings:
        st.warning(r)
else:
    st.success("Ready to save!")

# Save button at bottom of the page.
save = st.button("Save", disabled=len(errors) != 0, type="primary")

pos_c = st.container()

# When click the save button, save the data.
if save:
    gpg = GamesPlaneGame(st.session_state.name, anchored, unanchored,
                         st.session_state.positions, st.session_state.cm_to_space, r"CameraCalibration\good_calibration.yaml")

    path = write_game(gpg)

    if uploaded_file is not None:
        save_uploaded_pdf(uploaded_file, f"./App/PDFs/{st.session_state.name}.pdf")

    st.write(f"Saved game to {path}!")
