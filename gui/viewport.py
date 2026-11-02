from models import Graph


class Viewport():
    def __init__(self, graph: Graph, width: int, height: int,
                 padding: int = 60) -> None:
        self._width = width
        self._height = height
        self._padding = padding

        xs = [zone.x for zone in graph.zones.values()]
        ys = [zone.y for zone in graph.zones.values()]

        self._min_x = min(xs)
        self._max_x = max(xs)
        self._min_y = min(ys)
        self._max_y = max(ys)
        self.resize(width, height)

    def resize(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        span_x = max(self._max_x - self._min_x, 1)
        span_y = max(self._max_y - self._min_y, 1)
        avail_w = max(width - 2 * self._padding, 1)
        avail_h = max(height - 2 * self._padding, 1)
        self.scale = min(avail_w / span_x,
                         avail_h / span_y)
        self._offset_x = self._padding + (avail_w - span_x *
                                          self.scale) / 2
        self._offset_y = self._padding + (avail_h - span_y *
                                          self.scale) / 2

    def to_screen(self, x: float, y: float) -> tuple[int, int]:
        px = self._offset_x + (x - self._min_x) * self.scale
        py = self._offset_y + (y - self._min_y) * self.scale
        return (round(px), round(py))
