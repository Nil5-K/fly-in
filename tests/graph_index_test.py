"""Tests for the graph index."""
from graph_index import GraphIndex
from models.models import Connection, Graph, Role, Zone, ZoneType


def make_graph(
    types: dict[str, ZoneType], links: list[tuple[str, str]]
) -> Graph:
    zones = {
        name: Zone(name, i, 0, Role.NORMAL, zone_type)
        for i, (name, zone_type) in enumerate(types.items())
    }
    first, last = list(zones)[0], list(zones)[-1]
    return Graph(
        nb_drones=1,
        zones=zones,
        connections=[Connection(a, b) for a, b in links],
        start=first,
        end=last,
    )


def test_move_cost() -> None:
    n = Zone("n", 0, 0, Role.NORMAL)
    r = Zone("r", 0, 0, Role.NORMAL, ZoneType.RESTRICTED)
    p = Zone("p", 0, 0, Role.NORMAL, ZoneType.PRIORITY)
    assert GraphIndex.move_cost(n) == 1
    assert GraphIndex.move_cost(r) == 2
    assert GraphIndex.move_cost(p) == 1


def test_edges_in_both_directions() -> None:
    graph = make_graph(
        {"a": ZoneType.NORMAL, "b": ZoneType.NORMAL}, [("a", "b")]
    )
    index = GraphIndex().build_index(graph)
    assert [e.target for e in index["a"]] == ["b"]
    assert [e.target for e in index["b"]] == ["a"]


def test_every_zone_has_an_entry() -> None:
    graph = make_graph(
        {"a": ZoneType.NORMAL, "b": ZoneType.NORMAL, "c": ZoneType.NORMAL},
        [("a", "b")],
    )
    index = GraphIndex().build_index(graph)
    assert set(index) == {"a", "b", "c"}
    assert index["c"] == []


def test_blocked_zone_is_never_a_target() -> None:
    graph = make_graph(
        {"a": ZoneType.NORMAL, "x": ZoneType.BLOCKED, "b": ZoneType.NORMAL},
        [("a", "x"), ("x", "b")],
    )
    index = GraphIndex().build_index(graph)
    assert index["a"] == []
    assert index["b"] == []
    # edges leaving the blocked zone are irrelevant, nobody can enter it
    assert all(e.target != "x" for edges in index.values() for e in edges)


def test_cost_depends_on_target_zone() -> None:
    graph = make_graph(
        {"a": ZoneType.NORMAL, "r": ZoneType.RESTRICTED},
        [("a", "r")],
    )
    index = GraphIndex().build_index(graph)
    assert index["a"][0].cost == 2  # a -> r enters restricted
    assert index["r"][0].cost == 1  # r -> a enters normal


def test_edge_keeps_connection() -> None:
    graph = make_graph(
        {"a": ZoneType.NORMAL, "b": ZoneType.NORMAL}, [("a", "b")]
    )
    index = GraphIndex().build_index(graph)
    assert index["a"][0].connection is graph.connections[0]
