from Helpers.DigitalAruco import *

class GamesPlaneGame:
    def __init__(self, camera_yaml):
        pass

    # Shortcut to pass an image to the gframe.
    def process_image(self, image):
        return self.gframe.process_image(image)
    
    # DEBUG Helper for now. Returns a text-based representation of the board.
    def to_board(self, pieces: list[DigitalAruco]) -> str:
        pass