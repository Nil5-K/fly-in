import heapq

from heuristic import Heuristic
from models.models import Edge, Graph, Step, ZoneType
from reservation_table import ReservationTable

State = tuple[str, int]


class TimeAStar():
    def __init__(
        self,
        graph: Graph,
        index: dict[str, list[Edge]],
        heuristic: Heuristic,
        table: ReservationTable,
        max_turn: int | None = None,
    ) -> None:
        self.graph = graph
        self._index = index
        self._heuristic = heuristic
        self.table = table
        start_h = heuristic.h(graph.start) or 0
        self.max_turn = (
            max_turn if max_turn is not None
            else start_h + 2 * graph.nb_drones + len(graph.zones)
        )

    def find_route(self) -> list[Step] | None:
        start: State = (self.graph.start, 0)
        start_h = self._heuristic.h(self.graph.start)
        if start_h is None:
            return None
        came_from: dict[State, tuple[State, Edge | None]] = {}
        best_bad: dict[State, int] = {start: 0}
        pq: list[tuple[int, int, int, str]] = [(start_h, 0, 0, start[0])]
        while pq:
            _, bad, t, zone = heapq.heappop(pq)
            if bad > best_bad[(zone, t)]:
                continue
            if zone == self.graph.end:
                return self._reconstruct(came_from, (zone, t))
            if t >= self.max_turn:
                continue
            for edge in self._moves(zone, t):
                self._push(pq, best_bad, came_from, (zone, t), bad, edge)
            if self.table.can_wait(zone, t):
                self._push(pq, best_bad, came_from, (zone, t), bad, None)
        return None

    def _moves(self, zone: str, t: int) -> list[Edge]:
        return [e for e in self._index[zone] if self.table.can_move(e, t)]

    def _push(
        self,
        pq: list[tuple[int, int, int, str]],
        best_bad: dict[State, int],
        came_from: dict[State, tuple[State, Edge | None]],
        current: State,
        bad: int,
        edge: Edge | None,
    ) -> None:
        zone, t = current
        if edge is None:
            nxt: State = (zone, t + 1)
        else:
            nxt = (edge.target, t + edge.cost)
            if self.graph.zones[edge.target].zone_type != ZoneType.PRIORITY:
                bad += 1
        h = self._heuristic.h(nxt[0])
        if h is None or (nxt in best_bad and best_bad[nxt] <= bad):
            return
        best_bad[nxt] = bad
        came_from[nxt] = (current, edge)
        heapq.heappush(pq, (nxt[1] + h, bad, nxt[1], nxt[0]))

    @staticmethod
    def _reconstruct(
        came_from: dict[State, tuple[State, Edge | None]], end: State
    ) -> list[Step]:
        steps: list[Step] = []
        state = end
        while state in came_from:
            prev, edge = came_from[state]
            steps.append(Step(prev[0], prev[1], edge))
            state = prev
        steps.reverse()
        return steps
