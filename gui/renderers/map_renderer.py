import pygame

from gui.viewport import Viewport
from models import Graph, Role


class MapRenderer():
    def __init__(self, graph: Graph, viewport: Viewport,
                 font: pygame.font.Font) -> None:
        self._graph = graph
        self._viewport = viewport
        self._font = font

    def draw(self, surface: pygame.Surface) -> None:
        self._draw_connections(surface)
        self._draw_zones(surface)

    def _draw_connections(self, surface: pygame.Surface) -> None:
        for conn in self._graph.connections:
            zone_a = self._graph.zones[conn.zone_a]
            zone_b = self._graph.zones[conn.zone_b]
            start = self._viewport.to_screen(zone_a.x, zone_a.y)
            end = self._viewport.to_screen(zone_b.x, zone_b.y)
            pygame.draw.line(surface, (120, 120, 120), start, end)

    def _draw_zones(self, surface: pygame.Surface) -> None:
        radius = max(6, min(20, round(self._viewport.scale * 0.3)))
        placed: list[pygame.Rect] = []
        labels: list[tuple[pygame.Surface, pygame.Rect]] = []
        for zone in self._graph.zones.values():
            pos = self._viewport.to_screen(zone.x, zone.y)
            try:
                if zone.color:
                    color = pygame.Color(zone.color)
                else:
                    color = pygame.Color("gray")
            except ValueError:
                color = pygame.Color("gray")
            pygame.draw.circle(surface, color, pos, radius)
            if zone.role in (Role.START, Role.END):
                pygame.draw.circle(surface, (255, 255, 255), pos, radius, 3)
            text = self._font.render(zone.name, True, (255, 255, 255))
            below = text.get_rect(midtop=(pos[0], pos[1] + radius + 4))
            above = text.get_rect(midbottom=(pos[0], pos[1] - radius - 4))
            for rect in (below, above):
                if rect.collidelist(placed) == -1:
                    placed.append(rect)
                    labels.append((text, rect))
                    break
        for text, rect in labels:
            surface.blit(text, rect)
