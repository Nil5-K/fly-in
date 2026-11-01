import heapq

from graph_index import GraphIndex
from models import Edge, Graph


class Heuristic():
    def __init__(self, graph: Graph, index: dict[str, list[Edge]]) -> None:
        self.graph = graph
        self.index = index
        self.dist = self.build_heuristic()

    def build_heuristic(self) -> dict[str, int]:
        goal = self.graph.end
        dist: dict[str, int] = {goal: 0}
        pq: list[tuple[int, str]] = [(0, goal)]
        while pq:
            d, v = heapq.heappop(pq)
            if d > dist[v]:
                continue
            step = GraphIndex.move_cost(self.graph.zones[v])
            for edge in self.index[v]:
                u = edge.target
                new_d = d + step
                if new_d < dist.get(u, new_d + 1):
                    dist[u] = new_d
                    heapq.heappush(pq, (new_d, u))
        return dist

    def h(self, zone: str) -> int | None:
        return self.dist.get(zone)
