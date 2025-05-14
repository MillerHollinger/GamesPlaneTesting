from Helpers.DigitalAruco import DigitalAruco

class UwapiConverter:
    # Converts a representation of the current turn and the seen DigitalArucos into a UWAPI string.
    # Return "fail" to reject the board state.
    @classmethod
    def convert(cls, turn: str, pieces: list[DigitalAruco]) -> str:
        return ""

class DaoConverter(UwapiConverter):
    @classmethod
    def convert(cls, turn: str, pieces: list[DigitalAruco]) -> str:
        if len(pieces) != 8:
            return "fail"

        board_str = "2_" if turn == "Black" else "1_"
        
        POS_TO_IDX = {
            2.7 : {
                2.7 : [3, 0],
                0.9 : [3, 1],
                -0.9 : [3, 2],
                -2.7 : [3, 3]
            },
            0.9 : {
                2.7 : [2, 0],
                0.9 : [2, 1],
                -0.9 : [2, 2],
                -2.7 : [2, 3]
            },
            -0.9 : {
                2.7 : [1, 0],
                0.9 : [1, 1],
                -0.9 : [1, 2],
                -2.7 : [1, 3]
            },
            -2.7 : {
                2.7 : [0, 0],
                0.9 : [0, 1],
                -0.9 : [0, 2],
                -2.7 : [0, 3]
            }
        }

        GRID = len(POS_TO_IDX)
        board_rep = [["-" for c in range(GRID)] for r in range(GRID)]

        for piece in pieces:
            name = "O" if piece.phys.id == 1 else "X"
            pos_x, pos_y = piece.closest_board_position
            idx_x, idx_y = POS_TO_IDX[pos_x][pos_y]
            board_rep[idx_x][idx_y] = name
        
        for y in range(GRID):
            for x in range(GRID):
                board_str += board_rep[x][y]
        
        return board_str