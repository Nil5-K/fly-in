from collections import defaultdict

from models import Graph, Edge


class ReservationTable():
    """Track how many drones use each zone and link at each turn.

    A zone or link is free at turn t while its count at t is below its
    capacity. The start and end zones can hold all the drones.
    """
    def __init__(self, graph: Graph) -> None:
        """Read the capacities from the graph.

        Args:
            graph: The parsed map.
        """
        self.graph = graph
        self.zone_count: defaultdict[tuple[str,
                                           int], int] = defaultdict(int)
        self.link_count: defaultdict[tuple[frozenset[str],
                                           int], int] = defaultdict(int)
        self._zone_capacity: dict[str, int] = {}
        self._link_capacity: dict[frozenset[str], int] = {}

        for conn in graph.connections:
            self._link_capacity[conn.key] = conn.max_link_capacity

        for name, zone in graph.zones.items():
            self._zone_capacity[name] = zone.max_drones
        self._zone_capacity[graph.start] = graph.nb_drones
        self._zone_capacity[graph.end] = graph.nb_drones

    def zone_free(self, zone: str, t: int) -> bool:
        """Check that a zone has room at a given turn.

        Args:
            zone: Zone name.
            t: Turn number.

        Returns:
            True if count(zone, t) < max_drones.
        """
        return self.zone_count.get((zone, t), 0) < self._zone_capacity[zone]

    def link_free(self, edge: Edge, t: int) -> bool:
        """Check that a link has room during a whole move.

        A move that starts at turn t and costs c uses the link on turns
        t+1 .. t+c, so every one of those turns must be below capacity.

        Args:
            edge: The edge to traverse.
            t: Turn the move starts.

        Returns:
            True if the link is free on all those turns.
        """
        key = edge.connection.key
        capacity = self._link_capacity[key]
        for turn in range(t + 1, t + edge.cost + 1):
            used = self.link_count.get((key, turn), 0)
            if used >= capacity:
                return False
        return True

    def can_wait(self, zone: str, t: int) -> bool:
        """Check that a drone can stay in a zone for one more turn.

        Args:
            zone: Zone name.
            t: Current turn.

        Returns:
            True if the zone has room at turn t+1.
        """
        return self.zone_free(zone, t + 1)

    def can_move(self, edge: Edge, t: int) -> bool:
        """Check that a drone can take an edge.

        The link must be free during the move and the target zone must
        have room at the arrival turn t + cost.

        Args:
            edge: The edge to traverse.
            t: Turn the move starts.

        Returns:
            True if the move is allowed.
        """
        return (self.link_free(edge, t)
                and self.zone_free(edge.target, t + edge.cost))

    def reserve_wait(self, zone: str, t: int) -> None:
        """Reserve a zone for one waiting turn (until t+1).

        Args:
            zone: Zone name.
            t: Turn the wait starts.
        """
        self.zone_count[(zone, t + 1)] += 1

    def reserve_move(self, edge: Edge, t: int) -> None:
        """Reserve the link and the arrival slot of a move.

        The link is used on turns t+1 .. t+cost and the target zone is
        used at turn t+cost.

        Args:
            edge: The edge that is traversed.
            t: Turn the move starts.
        """
        key = edge.connection.key
        for turn in range(t + 1, t + edge.cost + 1):
            self.link_count[(key, turn)] += 1
        self.zone_count[(edge.target, t + edge.cost)] += 1
