import math


class Playback():
    """Simulation clock where one second is one turn."""
    def __init__(self, total_turns: int):
        """Start the clock at time 0, playing.

        Args:
            total_turns: Length of the simulation in turns.
        """
        self.total_turns = total_turns
        self.sim_time: float = 0.0
        self.paused: bool = False

    def update(self, dt: float) -> None:
        """Advance the clock by dt seconds.

        The time is capped at total_turns, where playback pauses.

        Args:
            dt: Seconds since the last frame.
        """
        if self.paused:
            return
        self.sim_time += dt
        self.sim_time = min(self.sim_time, self.total_turns)
        if self.sim_time >= self.total_turns:
            self.paused = True

    def toggle(self) -> None:
        """Pause or resume, restarting from 0 if the end was reached."""
        if self.paused:
            if self.sim_time >= self.total_turns:
                self.sim_time = 0.0
            self.paused = False
        else:
            self.paused = True

    def stop(self) -> None:
        """Go back to turn 0 and pause."""
        self.sim_time = 0
        self.paused = True

    def skip_forward(self) -> None:
        """Jump to the start of the next turn: floor(t) + 1."""
        self.sim_time = min(math.floor(self.sim_time) + 1, self.total_turns)

    def skip_back(self) -> None:
        """Jump to the start of the previous turn: ceil(t) - 1."""
        self.sim_time = max(math.ceil(self.sim_time) - 1, 0)
