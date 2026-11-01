from collections import defaultdict

from models import Graph, Edge


class ReservationTable():
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.zone_count: defaultdict[tuple[str,
                                           int], int] = defaultdict(int)
        self.link_count: defaultdict[tuple[frozenset[str],
                                           int], int] = defaultdict(int)
        self.zone_capacity: dict[str, int] = {}
        self.link_capacity: dict[frozenset[str], int] = {}

        for conn in graph.connections:
            self.link_capacity[conn.key] = conn.max_link_capacity

        for name, zone in graph.zones.items():
            self.zone_capacity[name] = zone.max_drones
        self.zone_capacity[graph.start] = graph.nb_drones
        self.zone_capacity[graph.end] = graph.nb_drones

    def zone_free(self, zone: str, t: int) -> bool:
        return self.zone_count.get((zone, t), 0) < self.zone_capacity[zone]

    def link_free(self, edge: Edge, t: int) -> bool:
        key = edge.connection.key
        capacity = self.link_capacity[key]
        for turn in range(t + 1, t + edge.cost + 1):
            used = self.link_count.get((key, turn), 0)
            if used >= capacity:
                return False
        return True

    def can_wait(self, zone: str, t: int) -> bool:
        return self.zone_free(zone, t + 1)

    def can_move(self, edge: Edge, t: int) -> bool:
        return (self.link_free(edge, t)
                and self.zone_free(edge.target, t + edge.cost))

    def reserve_wait(self, zone: str, t: int) -> None:
        self.zone_count[(zone, t + 1)] += 1

    def reserve_move(self, edge: Edge, t: int) -> None:
        key = edge.connection.key
        for turn in range(t + 1, t + edge.cost + 1):
            self.link_count[(key, turn)] += 1
        self.zone_count[(edge.target, t + edge.cost)] += 1
