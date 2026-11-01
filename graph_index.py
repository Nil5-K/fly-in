from models import Edge, Graph, ZoneType, Zone


class GraphIndex():
    @staticmethod
    def move_cost(target: Zone) -> int:
        if target.zone_type == ZoneType.RESTRICTED:
            return 2
        return 1

    def build_index(self, graph: Graph) -> dict[str, list[Edge]]:
        index: dict[str, list[Edge]] = {name: [] for name in graph.zones}
        for conn in graph.connections:
            for src, dst in ((conn.zone_a, conn.zone_b),
                             (conn.zone_b, conn.zone_a)):
                target = graph.zones[dst]
                if target.zone_type == ZoneType.BLOCKED:
                    continue
                index[src].append(Edge(conn, dst, self.move_cost(target)))
        return index
