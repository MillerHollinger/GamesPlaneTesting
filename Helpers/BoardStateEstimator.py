class BoardStateEstimator:
    def __init__(self, existing: list = []):
        self.records = []

    def add_record(self, board_state, time):
        self.records.append(BoardStateRecord(board_state, time))

    # Gives this BSE's best guess at the board state with its current information.
    # To be filled in by deriving classes.
    def estimate(self):
        return self.records[-1].state_estimate

class BoardStateRecord:
    # Provide time in seconds
    def __init__(self, state_estimate, time: float):
        self.state_estimate = state_estimate
        self.time = time

# Example BSE
# Makes its estimate using the last X seconds of data.
# Whatever the most common guess, it says is true.
class LastSeconds(BoardStateEstimator):
    def estimate(self, seconds: float = 2.0):
        end_time = self.records[-1].time
        min_time = end_time - seconds

        index = len(self.records)

        # Find the lowest index above min_time
        min_index = index
        while index >= 0 and self.records[index].time >= min_time:
            min_index = index
            index = index - 1
        
        usable_estimates = self.records[min_index:]
        votes = {}
        max = 0
        max_est = []

        for est in usable_estimates:
            if est in votes.keys():
                votes[est] += 1
            else:
                votes[est] = 1
            if votes[est] >= max: # Equals lets later pictures break ties
                max = votes[est]
                max_est = est

        return max_est

