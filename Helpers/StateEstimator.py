import time
from collections import deque, Counter

# Interface for Estimators
class BoardStateEstimator:
    
    def seen_board_state(self, board: str, timest=None) -> None:
        return
    def curr_board_state(self) -> str:
        return

## Sliding window (majority vote) Estimator
class MajorityEstimator(BoardStateEstimator):

    def __init__(self, max_frames=99, max_seconds=None):
        self.max_frames  = max_frames
        self.max_seconds = max_seconds
        self.queue = deque()  # Entries = (timestamp, board_str)

    def seen_board_state(self, board, timest=None):
        if timest is None:
            timest = time.time()
        self.queue.append((timest, board))
        self.cleanup()

    def has_state(self):
        return bool(self.queue)

    def curr_board_state(self):
        self.cleanup()
        if not self.queue:
            raise Exception("No valid board states in my queue")

        boards = [b for t, b in self.queue]
        winner, c = Counter(boards).most_common(1)[0]
        return winner

    def cleanup(self):
        if self.max_frames is not None:
            while len(self.queue) > self.max_frames:
                self.queue.popleft()

        if self.max_seconds is not None:
            min = time.time() - self.max_seconds
            while self.queue and self.queue[0][0] < min:
                self.queue.popleft()

## Agreeing (x agreeing frames changes state)
class AgreeingEstimator(BoardStateEstimator):

    def __init__(self, min_frames=9):
        self.min_frames = min_frames
        self.curr_state = None
        self.cleanup()

    def seen_board_state(self, board, timest=None):
        # Initialize
        if self.curr_state is None:
            self.curr_state = board
        # Same state
        if self.curr_state == board:
            self.cleanup()
        else: # New state
            if self.new_state == board:
                self.new_count += 1
                if self.new_count >= self.min_frames:
                    self.curr_state = self.new_state
                    self.cleanup()
            else:
                self.new_state = board
                self.new_count = 1

    def curr_board_state(self):
        return self.curr_state
    
    def cleanup(self):
        self.new_state = None
        self.new_count = 0

# Combination (ensemble of multiple) Estimator
class CombinationEstimator(BoardStateEstimator):

    def __init__(self, estimators: list[BoardStateEstimator]):
        self.estimators = estimators

    def seen_board_state(self, board, timest=None):
        for e in self.estimators:
            e.seen_board_state(board, timest)

    def curr_board_state(self):
        states = [e.curr_board_state() for e in self.estimators]
        winner, c = Counter(states).most_common(1)[0]
        return winner