"""
Implement a state estimator with an algorithm that settles on the most stable board

Gotta make our state machine resistant to outlier frames that misdetect "movement"

Any idea how we should do that algorithm? Like it has to stay the same for 1 second

Yeah I was thinking for a certain latency (x seconds, x frames, whatever) we take the majority vote of the detections
Or option 2 is after x frames of detecting a different board state it says okay that's probably the new detected state

The main issue is sometimes it flip flops a bunch between possible states especially if the camera is at a weird angle
I guess there's not too much we can do about that though. Maybe we should have the decision maker be a separate class:

BoardStateEstimator
    Has a function to indicate a board state as seen in a single picture and the time at which it was detected
    Has a function to get its best guess of what the real board state currently is

Then we can switch those estimators out and try different approaches
Maybe an estimator that combines several other estimator's guesses
"""

import time
from collections import deque, Counter

class BoardStateEstimator:
    def seen_board_state(self, board, timestamp=None):
        return
    def curr_board_state(self, now_timestamp=None):
        return


## Sliding window (majority vote) Estimator
class MajorityEstimator(BoardStateEstimator):

    def __init__(self, window_seconds=1.0):
        self.window_seconds = window_seconds
        self.history = deque()   # Each entry: (timestamp, board)

    def seen_board_state(self, board, timestamp=None):
        timestamp = timestamp if timestamp is not None else time.time()
        self.history.append((timestamp, board))

    def curr_board_state(self, now_timestamp=None):
        now_timestamp = now_timestamp if now_timestamp is not None else time.time()
        # Discard old frames
        min_allowed = now_timestamp - self.window_seconds
        while self.history and self.history[0][0] < min_allowed:
            self.history.popleft()
        if not self.history:
            return None   # Not enough data

        boards = [b for _,b in self.history]
        most_common, count = Counter(boards).most_common(1)[0]
        return most_common


## Sticky (x agreeing frames changes state)
class StickyEstimator(BoardStateEstimator):

    def __init__(self, min_consecutive_frames=5):
        self.min_consecutive_frames = min_consecutive_frames
        self.current_state = None
        self.candidate_state = None
        self.candidate_count = 0

    def seen_board_state(self, board, timestamp=None):
        # We don't need timestamp in this approach, but it could be tracked if needed
        if self.current_state is None:
            self.current_state = board
            self.candidate_state = None
            self.candidate_count = 0
        elif board == self.current_state:
            # Consistent with current
            self.candidate_state = None
            self.candidate_count = 0
        else:
            # Candidate for new state
            if board == self.candidate_state:
                self.candidate_count += 1
                if self.candidate_count >= self.min_consecutive_frames:
                    self.current_state = self.candidate_state
                    self.candidate_state = None
                    self.candidate_count = 0
            else:
                self.candidate_state = board
                self.candidate_count = 1

    def curr_board_state(self, now_timestamp=None):
        return self.current_state


# Combination (ensemble of multiple) Estimator
class CombinationEstimator(BoardStateEstimator):

    def __init__(self, estimators):
        self.estimators = estimators

    def seen_board_state(self, board, timestamp=None):
        for e in self.estimators:
            e.seen_board_state(board, timestamp)

    def get_current_board_state(self, now_timestamp=None):
        states = [e.get_current_board_state(now_timestamp) for e in self.estimators]
        most_common, count = Counter(states).most_common(1)[0]
        return most_common