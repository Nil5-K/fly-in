from models import Graph, Step, Edge
from heuristic import Heuristic
from time_a_star import TimeAStar
from reservation_table import ReservationTable


class PlanningError(Exception):
    pass


class Planer():
    def __init__(self, graph: Graph, index: dict[str, list[Edge]],
                 heuristic: Heuristic, table: ReservationTable) -> None:
        self.graph = graph
        self.index = index
        self.heuristic = heuristic
        self.table = table

    def plan(self) -> list[list[Step]]:
        routes = []
        for drone in range(1, self.graph.nb_drones + 1):
            route = TimeAStar(
                self.graph, self.index, self.heuristic, self.table
                ).find_route()
            if route is None:
                raise PlanningError(f"no route found for D{drone}")
            self._reserver(route)
            routes.append(route)
        return routes

    def _reserver(self, route: list[Step]) -> None:
        for step in route:
            if step.edge is None:
                self.table.reserve_wait(step.zone, step.t)
            else:
                self.table.reserve_move(step.edge, step.t)

    @staticmethod
    def to_turns(routes: list[list[Step]]) -> list[str]:
        turns: dict[int, list[str]] = {}
        for drone, route in enumerate(routes, start=1):
            for step in route:
                if step.edge is None:
                    continue
                for dt in range(1, step.edge.cost):
                    turns.setdefault(step.t + dt, []).append(
                        f"D{drone}-{step.edge.connection.name}"
                    )
                turns.setdefault(step.t + step.edge.cost, []).append(
                    f"D{drone}-{step.edge.target}"
                )
        last = max(turns, default=0)
        return [" ".join(turns.get(t, [])) for t in range(1, last + 1)]
