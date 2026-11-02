import pygame

from gui.renderers.map_renderer import MapRenderer
from gui.renderers.drone_renderer import DroneRenderer
from gui.renderers.hud_renderer import HudRenderer
from gui.viewport import Viewport
from gui.playback import Playback
from models import Graph, Step


class Renderer():
    def __init__(self, graph: Graph, viewport: Viewport,
                 routes: list[list[Step]], total_turns: int) -> None:
        self._font = pygame.font.Font(None, 20)
        self._map = MapRenderer(graph, viewport, self._font)
        self._drone = DroneRenderer(graph, routes, viewport, self._font)
        self.hud = HudRenderer(total_turns)

    def draw(self, surface: pygame.Surface, playback: Playback) -> None:
        surface.fill((20, 20, 30))
        self._map.draw(surface)
        self._drone.draw(surface, playback.sim_time)
        self.hud.draw(surface, playback)
