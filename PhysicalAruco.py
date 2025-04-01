# An PhysicalAruco represents the various info about a specific physical Aruco marker.

class PhysicalAruco:
    def __init__(self, id, tag, size, anchored, board_position=None):
        # This aruco's id, defined by the aruco dictionary.
        self.id = id

        # This aruco's tag. This is supplementary info used to turn it into a board state for UWAPI.
        # You can use whatever you like for this.
        self.tag = tag

        # 
        self.size = size
        self.anchored = anchored
        self.board_position = board_position

        if self.anchored and board_position == None:
            raise Exception("PhysicalAruco: Anchored PhysicalArucos must have a provided board_position.")
        
        return
    
    # Shortcut to quickly define several ArucoDefinitions.
    @staticmethod
    def generate_many(ids, tag, size, anchored, board_positions):
        return [PhysicalAruco(id, tag, size, anchored, pos) for id, pos in zip(ids, board_positions)]