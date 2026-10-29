import pygame

from gui.renderers.map_renderer import MapRenderer
from gui.viewport import Viewport
from models.models import Graph


class Renderer():
    def __init__(self, graph: Graph, viewport: Viewport) -> None:
        self.map = MapRenderer(graph, viewport)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((20, 20, 30))
        self.map.draw(surface)
