from Helpers.GamesFrame import *
from Helpers.PhysicalBoardInfo import *
from Helpers.PhysicalAruco import *

class GamesPlaneGame:
    def __init__(self, name: str, anchored_arucos: list[PhysicalAruco], unanchored_arucos: list[PhysicalAruco], 
                 valid_positions: list[tuple[float, float]], cm_to_space: float, camera_yaml: str):
        self.name = name
        self.board_info = PhysicalBoardInfo(
            unanchored_arucos,
            anchored_arucos,
            valid_positions,
            cm_to_space
        )
        self.camera_yaml = camera_yaml
        self.gframe = GamesFrame(camera_yaml, self.board_info)
        return

    # Shortcut to pass an image to the gframe.
    def process_image(self, image, reason=True):
        return self.gframe.process_image(image, reason)
    
    # DEBUG Helper for now. Returns a text-based representation of the board.
    def to_board(self, pieces: list[DigitalAruco]) -> str:
        pass