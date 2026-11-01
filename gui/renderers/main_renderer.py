import pygame

from gui.renderers.map_renderer import MapRenderer
from gui.viewport import Viewport
from models import Graph


class Renderer():
    def __init__(self, graph: Graph, viewport: Viewport) -> None:
        self.font = pygame.font.Font(None, 20)
        self.map = MapRenderer(graph, viewport, self.font)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((20, 20, 30))
        self.map.draw(surface)
