import sys

import pygame

from gui.renderers.main_renderer import Renderer
from gui.viewport import Viewport
from parser import Parser, ParsingError


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <map_file>", file=sys.stderr)
        return 1

    try:
        graph = Parser(sys.argv[1]).parse()
    except (OSError, ParsingError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    pygame.init()
    width, height = 1000, 700
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("fly-in")
    clock = pygame.time.Clock()

    viewport = Viewport(graph, width, height)
    renderer = Renderer(graph, viewport)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                viewport.resize(event.w, event.h)

        renderer.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
