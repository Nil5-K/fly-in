import sys

import pygame

from graph_index import GraphIndex
from gui import Renderer, Viewport, Playback
from heuristic import Heuristic
from models import Graph, Step
from parser import Parser, ParsingError
from planner import Planer, PlanningError
from reservation_table import ReservationTable


class App():
    """Run the planner on a map file and show the result in a window."""
    def __init__(self, argv: list[str]) -> None:
        """Store the command line arguments.

        Args:
            argv: Command line arguments, including the program name.
        """
        self._argv = argv
        self._screen: pygame.Surface
        self._viewport: Viewport
        self._renderer: Renderer
        self._playback: Playback
        self._running = False

    def run(self) -> int:
        """Parse the map, plan the routes, print them and open the GUI.

        Returns:
            Exit code: 0 on success, 1 on a usage, parsing, planning or
            display error, 130 on keyboard interrupt.
        """
        if len(self._argv) != 2:
            print(f"usage: {self._argv[0]} <map_file>", file=sys.stderr)
            return 1

        try:
            graph = Parser(self._argv[1]).parse()
        except (OSError, ParsingError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        index = GraphIndex().build_index(graph)
        heuristic = Heuristic(graph, index)
        planner = Planer(graph, index, heuristic, ReservationTable(graph))
        try:
            routes = planner.plan()
        except PlanningError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        for line in planner.to_turns(routes):
            print(line)

        try:
            self._run_gui(graph, routes)
        except (pygame.error, OSError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except KeyboardInterrupt:
            return 130
        finally:
            pygame.quit()
        return 0

    def _run_gui(self, graph: Graph, routes: list[list[Step]]) -> None:
        """Open the window and run the main loop until it is closed.

        The total number of turns is the latest arrival time over all
        drones: max(step.t + edge.cost).

        Args:
            graph: The parsed map.
            routes: One list of steps per drone.
        """
        pygame.init()
        width, height = 1000, 700
        self._screen = pygame.display.set_mode(
            (width, height), pygame.RESIZABLE)
        pygame.display.set_caption("fly-in")
        clock = pygame.time.Clock()

        total_turns = max(
            (step.t + step.edge.cost
             for route in routes for step in route if step.edge),
            default=0,
            )
        self._viewport = Viewport(graph, width, height)
        self._renderer = Renderer(graph, self._viewport, routes, total_turns)
        self._playback = Playback(total_turns)

        self._running = True
        while self._running:
            dt = clock.tick(60) / 1000
            for event in pygame.event.get():
                self._handle_event(event)
            self._playback.update(dt)
            self._renderer.draw(self._screen, self._playback)
            pygame.display.flip()

    def _handle_event(self, event: pygame.event.Event) -> None:
        """React to a single pygame event.

        Args:
            event: Quit, escape, resize, space or left click.
        """
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._running = False
        elif event.type == pygame.VIDEORESIZE:
            self._viewport.resize(event.w, event.h)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._playback.toggle()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)

    def _handle_click(self, pos: tuple[int, int]) -> None:
        """Run the playback action of the HUD button at a click.

        Args:
            pos: Mouse position in screen pixels.
        """
        action = self._renderer.hud.button_at(self._screen, pos)
        if action == "play":
            self._playback.toggle()
        elif action == "stop":
            self._playback.stop()
        elif action == "left_skip":
            self._playback.skip_back()
        elif action == "right_skip":
            self._playback.skip_forward()


if __name__ == "__main__":
    sys.exit(App(sys.argv).run())
