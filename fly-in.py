import sys

import pygame

from graph_index import GraphIndex
from gui import Renderer, Viewport, Playback
from heuristic import Heuristic
from models import Graph, Step
from parser import Parser, ParsingError
from planner import Planer, PlanningError
from reservation_table import ReservationTable


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <map_file>", file=sys.stderr)
        return 1

    try:
        graph = Parser(sys.argv[1]).parse()
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
        run_gui(graph, routes)
    except (pygame.error, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    finally:
        pygame.quit()
    return 0


def run_gui(graph: Graph, routes: list[list[Step]]) -> None:
    pygame.init()
    width, height = 1000, 700
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("fly-in")
    clock = pygame.time.Clock()

    total_turns = max(
        (step.t + step.edge.cost
         for route in routes for step in route if step.edge),
        default=0,
        )
    viewport = Viewport(graph, width, height)
    renderer = Renderer(graph, viewport, routes, total_turns)
    playback = Playback(total_turns)

    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                viewport.resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                playback.toggle()
            elif (event.type == pygame.MOUSEBUTTONDOWN
                  and event.button == 1):
                action = renderer.hud.button_at(screen, event.pos)
                if action == "play":
                    playback.toggle()
                elif action == "stop":
                    playback.stop()
                elif action == "left_skip":
                    playback.skip_back()
                elif action == "right_skip":
                    playback.skip_forward()

        playback.update(dt)
        renderer.draw(screen, playback)
        pygame.display.flip()


if __name__ == "__main__":
    sys.exit(main())
