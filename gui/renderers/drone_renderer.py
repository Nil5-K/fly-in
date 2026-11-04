import pygame

from gui.constants import ASSETS
from gui.viewport import Viewport
from models import Graph, Step


class DroneRenderer():
    """Draw the drones at their position for the current time."""
    def __init__(self, graph: Graph, routes: list[list[Step]],
                 viewport: Viewport, font: pygame.font.Font) -> None:
        """Load the drone sprite.

        Args:
            graph: The parsed map.
            routes: One list of steps per drone.
            viewport: Map to screen conversion.
            font: Font for the drone labels.
        """
        self._graph = graph
        self._routes = routes
        self._viewport = viewport
        self._font = font
        self._drone_img = pygame.image.load(ASSETS /
                                            "drone.png").convert_alpha()
        self._scaled: dict[int, pygame.Surface] = {}

    def _sprite(self) -> pygame.Surface:
        """Return the sprite scaled to the current zoom.

        The width is 0.6 * scale limited to 16..64 pixels and the height
        keeps the image ratio. Scaled images are cached by width.

        Returns:
            The scaled sprite.
        """
        width = max(16, min(64, round(self._viewport.scale * 0.6)))
        if width not in self._scaled:
            ratio = self._drone_img.get_height() / self._drone_img.get_width()
            self._scaled[width] = pygame.transform.smoothscale(
                self._drone_img, (width, round(width * ratio))
            )
        return self._scaled[width]

    def draw(self, surface: pygame.Surface, sim_time: float) -> None:
        """Draw every drone with its label.

        Args:
            surface: Surface to draw on.
            sim_time: Current simulation time in turns.
        """
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
        """Return the map position of a drone at time t.

        While a move runs the position is a linear interpolation between
        the two zones: a + (b - a) * f, with f = (t - step.t) / cost.
        While waiting it stays in the zone. After the last step it stays
        in the final zone.

        Args:
            route: Steps of the drone.
            t: Simulation time in turns.

        Returns:
            (x, y) in map coordinates.
        """
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
