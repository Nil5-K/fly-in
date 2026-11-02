import math


class Playback():
    def __init__(self, total_turns: int):
        self.total_turns = total_turns
        self.sim_time: float = 0.0
        self.paused: bool = False

    def update(self, dt: float) -> None:
        if self.paused:
            return
        self.sim_time += dt
        self.sim_time = min(self.sim_time, self.total_turns)
        if self.sim_time >= self.total_turns:
            self.paused = True

    def toggle(self) -> None:
        if self.paused:
            if self.sim_time >= self.total_turns:
                self.sim_time = 0.0
            self.paused = False
        else:
            self.paused = True

    def stop(self) -> None:
        self.sim_time = 0
        self.paused = True

    def skip_forward(self) -> None:
        self.sim_time = min(math.floor(self.sim_time) + 1, self.total_turns)

    def skip_back(self) -> None:
        self.sim_time = max(math.ceil(self.sim_time) - 1, 0)
