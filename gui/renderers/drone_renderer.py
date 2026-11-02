import pygame

from gui.constants import ASSETS
from gui.viewport import Viewport
from models import Graph, Step


class DroneRenderer():
    def __init__(self, graph: Graph, routes: list[list[Step]],
                 viewport: Viewport, font: pygame.font.Font) -> None:
        self._graph = graph
        self._routes = routes
        self._viewport = viewport
        self._font = font
        self._drone_img = pygame.image.load(ASSETS /
                                            "drone.png").convert_alpha()
        self._scaled: dict[int, pygame.Surface] = {}

    def _sprite(self) -> pygame.Surface:
        width = max(16, min(64, round(self._viewport.scale * 0.6)))
        if width not in self._scaled:
            ratio = self._drone_img.get_height() / self._drone_img.get_width()
            self._scaled[width] = pygame.transform.smoothscale(
                self._drone_img, (width, round(width * ratio))
            )
        return self._scaled[width]

    def draw(self, surface: pygame.Surface, sim_time: float) -> None:
        sprite = self._sprite()
        for i, route in enumerate(self._routes, start=1):
            x, y = self._position(route, sim_time)
            pos = self._viewport.to_screen(x, y)
            surface.blit(sprite, sprite.get_rect(center=pos))
            label = self._font.render(f"D{i}", True, (255, 255, 255))
            surface.blit(label, label.get_rect(
                midtop=(pos[0], pos[1] + sprite.get_height() // 2))
                )

    def _position(self, route: list[Step], t: float) -> tuple[float, float]:
        zones = self._graph.zones
        for step in route:
            time = 1 if step.edge is None else step.edge.cost
            if step.t <= t < step.t + time:
                a = zones[step.zone]
                if step.edge is None:
                    return (a.x, a.y)
                b = zones[step.edge.target]
                f = (t - step.t) / time
                return (a.x + (b.x - a.x) * f,
                        a.y + (b.y - a.y) * f)
        last = route[-1]
        end = zones[last.edge.target] if last.edge else zones[last.zone]
        return (end.x, end.y)
