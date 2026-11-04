import heapq

from graph_index import GraphIndex
from models import Edge, Graph


class Heuristic():
    """Distance-to-goal estimate for the time-expanded A*."""
    def __init__(self, graph: Graph, index: dict[str, list[Edge]]) -> None:
        """Precompute the distance from every zone to the end zone.

        Args:
            graph: The parsed map.
            index: Adjacency list from GraphIndex.
        """
        self._graph = graph
        self._index = index
        self._dist = self._build_heuristic()

    def _build_heuristic(self) -> dict[str, int]:
        """Run Dijkstra backwards from the end zone.

        Moving from u to v costs move_cost(v), so the recurrence is
        dist[u] = min(dist[v] + move_cost(v)) over all edges u -> v,
        with dist[end] = 0. Zone and link capacities are ignored, so the
        value never overestimates the real time and A* stays optimal.

        Returns:
            Dict from zone name to its minimal number of turns.
        """
        goal = self._graph.end
        dist: dict[str, int] = {goal: 0}
        pq: list[tuple[int, str]] = [(0, goal)]
        while pq:
            d, v = heapq.heappop(pq)
            if d > dist[v]:
                continue
            step = GraphIndex.move_cost(self._graph.zones[v])
            for edge in self._index[v]:
                u = edge.target
                new_d = d + step
                if new_d < dist.get(u, new_d + 1):
                    dist[u] = new_d
                    heapq.heappush(pq, (new_d, u))
        return dist

    def h(self, zone: str) -> int | None:
        """Return the estimated turns from a zone to the end zone.

        Args:
            zone: Zone name.

        Returns:
            The distance, or None if the end zone is unreachable.
        """
        return self._dist.get(zone)
