from models import Edge, Graph, ZoneType, Zone


class GraphIndex():
    """Build the adjacency list used by the path search."""
    @staticmethod
    def move_cost(target: Zone) -> int:
        """Return the number of turns needed to enter a zone.

        Restricted zones cost 2 turns, every other zone costs 1.

        Args:
            target: The zone being entered.

        Returns:
            The cost in turns.
        """
        if target.zone_type == ZoneType.RESTRICTED:
            return 2
        return 1

    def build_index(self, graph: Graph) -> dict[str, list[Edge]]:
        """Map each zone name to the edges leaving it.

        Connections are two-way, so each one gives two directed edges.
        Edges that lead into a blocked zone are left out.

        Args:
            graph: The parsed map.

        Returns:
            Dict from zone name to its list of outgoing edges.
        """
        index: dict[str, list[Edge]] = {name: [] for name in graph.zones}
        for conn in graph.connections:
            for src, dst in ((conn.zone_a, conn.zone_b),
                             (conn.zone_b, conn.zone_a)):
                target = graph.zones[dst]
                if target.zone_type == ZoneType.BLOCKED:
                    continue
                index[src].append(Edge(conn, dst, self.move_cost(target)))
        return index
