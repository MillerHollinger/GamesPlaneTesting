import streamlit as st

# Title
st.set_page_config(page_title="Welcome to GamesPlane")

# Help info

"""
# HOME SCREEN
At the home screen, you can see all of the GamesPlane Projects you have on your systems.
Each is represented by a name and image.

Each GamesPlane Project has:
- GamesPlane - The board you play on. Usually a PDF you can print out.
- GamesFrame - The information about the board and pieces.
- Files - Files used to make stuff related to the game, like pieces or the board.


# PROJECT PAGE
The project view lets you see the parts of your project.

Edit GamesPlane: Lets you load in a PDF to use as your board.
It identifies anchor arucos and lets you edit their position information.
It also lets you define spaces on the board.

Play Game: Starts a live video feed with the selected game.
You can select to use an image or video on your computer instead, and it will run on that.


# PLAY PROJECT
Starts a live video feed for the game.
Runs the pipeline on the resulting images.

"""