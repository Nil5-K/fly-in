from models import Graph, Step, Edge
from heuristic import Heuristic
from time_a_star import TimeAStar
from reservation_table import ReservationTable


class PlanningError(Exception):
    """Raised when a drone cannot be routed to the end zone."""
    pass


class Planer():
    """Plan a route for every drone, one after the other."""
    def __init__(self, graph: Graph, index: dict[str, list[Edge]],
                 heuristic: Heuristic, table: ReservationTable) -> None:
        """Store the shared planning data.

        Args:
            graph: The parsed map.
            index: Adjacency list from GraphIndex.
            heuristic: Distance-to-goal estimate.
            table: Reservation table, filled as routes are planned.
        """
        self._graph = graph
        self._index = index
        self._heuristic = heuristic
        self._table = table

    def plan(self) -> list[list[Step]]:
        """Find a route for each drone and reserve it.

        Drones are planned in order. Each new route has to avoid the
        reservations of the earlier ones, so capacities are never exceeded.

        Returns:
            One list of steps per drone.

        Raises:
            PlanningError: If a drone has no route.
        """
        routes = []
        for drone in range(1, self._graph.nb_drones + 1):
            route = TimeAStar(
                self._graph, self._index, self._heuristic, self._table
                ).find_route()
            if route is None:
                raise PlanningError(f"no route found for D{drone}")
            self._reserve(route)
            routes.append(route)
        return routes

    def _reserve(self, route: list[Step]) -> None:
        """Mark every step of a route as used in the table.

        Args:
            route: The steps of one drone.
        """
        for step in route:
            if step.edge is None:
                self._table.reserve_wait(step.zone, step.t)
            else:
                self._table.reserve_move(step.edge, step.t)

    @staticmethod
    def to_turns(routes: list[list[Step]]) -> list[str]:
        """Convert routes into the simulation output, one line per turn.

        A move of cost c that starts at turn t is written as D<n>-<link>
        for turns t+1 .. t+c-1 and as D<n>-<zone> at turn t+c, when the
        drone arrives. Waiting is not written.

        Args:
            routes: One list of steps per drone.

        Returns:
            One string per turn, with the moves separated by spaces.
        """
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
