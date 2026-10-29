import pygame

from gui.viewport import Viewport
from models.models import Graph, Role


class MapRenderer():
    def __init__(self, graph: Graph, viewport: Viewport) -> None:
        self.graph = graph
        self.viewport = viewport
        self.font = pygame.font.Font(None, 20)

    def draw(self, surface: pygame.Surface) -> None:
        self._draw_connections(surface)
        self._draw_zones(surface)

    def _draw_connections(self, surface: pygame.Surface) -> None:
        for conn in self.graph.connections:
            zone_a = self.graph.zones[conn.zone_a]
            zone_b = self.graph.zones[conn.zone_b]
            start = self.viewport.to_screen(zone_a.x, zone_a.y)
            end = self.viewport.to_screen(zone_b.x, zone_b.y)
            pygame.draw.line(surface, (120, 120, 120), start, end)

    def _draw_zones(self, surface: pygame.Surface) -> None:
        for zone in self.graph.zones.values():
            pos = self.viewport.to_screen(zone.x, zone.y)
            try:
                if zone.color:
                    color = pygame.Color(zone.color)
                else:
                    color = pygame.Color("gray")
            except ValueError:
                color = pygame.Color("gray")
            radius = 20
            pygame.draw.circle(surface, color, pos, radius)
            if zone.role in (Role.START, Role.END):
                pygame.draw.circle(surface, (255, 255, 255), pos, radius, 3)
            text = self.font.render(zone.name, True, (255, 255, 255))
            rect = text.get_rect(midtop=(pos[0], pos[1] + radius + 4))
            surface.blit(text, rect)
