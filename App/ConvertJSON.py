# Contains helpers to convert gamesplane info back and forth from json.
import json
import os

from Games.GamesPlaneGame import GamesPlaneGame
from Helpers.PhysicalAruco import PhysicalAruco

def build_arucos(aruco_data: list):
    return [PhysicalAruco(v["id"], v["tag"], v["size"], v["anchored"], v["position"]) for v in aruco_data]
    
# Given a path to a json game representation, return the resulting python object.
def fetch_game(game_name: str, camera_yaml: str = r"Camera Calibration\good_calibration.yaml"):
    json_path = r'.\App\ProjectData' + "\\" + game_name + ".json"
    with open(json_path, "r") as file:
        data = json.load(file)

    unanchored = build_arucos(data["aruco_unanchored"])
    anchored = build_arucos(data["aruco_anchored"])

    return GamesPlaneGame(
        data["name"],
        anchored,
        unanchored,
        data["valid_positions"],
        data["cm_to_space"],
        camera_yaml
    )

def dictify_aruco(aruco_object: PhysicalAruco):
    return {
        "id" : aruco_object.id,
        "tag" : aruco_object.tag,
        "size" : aruco_object.size,
        "anchored" : aruco_object.anchored,
        "position" : aruco_object.board_position
    }

# Given a GPG, saves it as a json object.
def write_game(gpg: GamesPlaneGame, path: str = None):
    to_write = {}

    to_write["name"] = gpg.name
    to_write["aruco_anchored"] = [dictify_aruco(aru) for aru in gpg.board_info.anchored_arucos]
    to_write["aruco_unanchored"] = [dictify_aruco(aru) for aru in gpg.board_info.unanchored_arucos]
    to_write["valid_positions"] = gpg.board_info.valid_board_positions
    to_write["cm_to_space"] = gpg.board_info.cm_to_space

    if path is None:
        path = gpg.name + ".json"

    with open(r'.\App\ProjectData' + "\\" + path, 'w') as file:
        json.dump(to_write, file, indent=4)

    return path


obj = fetch_game("Tic Tac Toe")
write_game(obj)