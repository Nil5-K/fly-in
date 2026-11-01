from models import Graph


class Viewport():
    def __init__(self, graph: Graph, width: int, height: int,
                 padding: int = 60) -> None:
        self.width = width
        self.height = height
        self.padding = padding

        xs = [zone.x for zone in graph.zones.values()]
        ys = [zone.y for zone in graph.zones.values()]

        self.min_x = min(xs)
        self.max_x = max(xs)
        self.min_y = min(ys)
        self.max_y = max(ys)
        self.resize(width, height)

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        span_x = max(self.max_x - self.min_x, 1)
        span_y = max(self.max_y - self.min_y, 1)
        avail_w = max(width - 2 * self.padding, 1)
        avail_h = max(height - 2 * self.padding, 1)
        self.scale = min(avail_w / span_x,
                         avail_h / span_y)
        self.offset_x = self.padding + (avail_w - span_x *
                                        self.scale) / 2
        self.offset_y = self.padding + (avail_h - span_y *
                                        self.scale) / 2

    def to_screen(self, x: int, y: int) -> tuple[int, int]:
        px = self.offset_x + (x - self.min_x) * self.scale
        py = self.offset_y + (y - self.min_y) * self.scale
        return (round(px), round(py))
