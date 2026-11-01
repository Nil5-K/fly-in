"""Tests for the reservation table."""
from models.models import Connection, Edge, Graph, Role, Zone, ZoneType
from reservation_table import ReservationTable


def build(link_capacity: int = 1) -> ReservationTable:
    """Graph: s - a - e and s - r - e, with a (cap 1) and r restricted."""
    zones = {
        "s": Zone("s", 0, 0, Role.START, max_drones=1),
        "a": Zone("a", 1, 0, Role.NORMAL, max_drones=1),
        "r": Zone("r", 1, 1, Role.NORMAL, ZoneType.RESTRICTED),
        "e": Zone("e", 2, 0, Role.END, max_drones=1),
    }
    conns = [
        Connection("s", "a", link_capacity),
        Connection("a", "e"),
        Connection("s", "r"),
        Connection("r", "e"),
    ]
    graph = Graph(3, zones, conns, "s", "e")
    return ReservationTable(graph)


def edge(table: ReservationTable, a: str, b: str) -> Edge:
    """Return the edge a -> b with the right turn cost."""
    conn = next(c for c in table.graph.connections
                if c.key == frozenset((a, b)))
    cost = 2 if table.graph.zones[b].zone_type == ZoneType.RESTRICTED else 1
    return Edge(conn, b, cost)


def test_empty_table_allows_everything() -> None:
    t = build()
    assert t.can_move(edge(t, "s", "a"), 0)
    assert t.can_wait("a", 0)


def test_zone_full_after_reservation() -> None:
    t = build()
    t.reserve_move(edge(t, "s", "a"), 0)   # a occupied at turn 1
    assert not t.zone_free("a", 1)
    assert t.zone_free("a", 2)


def test_second_drone_cannot_enter_full_zone() -> None:
    t = build(link_capacity=2)
    t.reserve_move(edge(t, "s", "a"), 0)
    assert not t.can_move(edge(t, "s", "a"), 0)


def test_link_capacity_blocks_other_drone() -> None:
    t = build(link_capacity=1)
    t.reserve_move(edge(t, "s", "a"), 0)
    assert not t.link_free(edge(t, "s", "a"), 0)
    assert t.link_free(edge(t, "s", "a"), 1)


def test_link_capacity_ignores_direction() -> None:
    t = build(link_capacity=1)
    t.reserve_move(edge(t, "s", "a"), 0)
    assert not t.link_free(edge(t, "a", "s"), 0)


def test_link_capacity_two_allows_two() -> None:
    t = build(link_capacity=2)
    t.reserve_move(edge(t, "s", "a"), 0)
    assert t.link_free(edge(t, "s", "a"), 0)
    t.reserve_move(edge(t, "s", "a"), 0)
    assert not t.link_free(edge(t, "s", "a"), 0)


def test_restricted_uses_link_two_turns_and_zone_on_arrival() -> None:
    t = build()
    t.reserve_move(edge(t, "s", "r"), 0)
    key = frozenset(("s", "r"))
    assert t.link_count[(key, 1)] == 1
    assert t.link_count[(key, 2)] == 1
    assert t.zone_count.get(("r", 1), 0) == 0   # in transit, in no zone
    assert t.zone_count[("r", 2)] == 1


def test_restricted_blocked_if_link_busy_in_second_turn() -> None:
    t = build()
    t.reserve_move(edge(t, "s", "r"), 1)   # link busy in turns 2 and 3
    assert not t.can_move(edge(t, "s", "r"), 0)


def test_leaving_frees_zone_same_turn() -> None:
    t = build()
    t.reserve_move(edge(t, "s", "a"), 0)   # a at turn 1
    t.reserve_move(edge(t, "a", "e"), 1)   # leaves a, e at turn 2
    assert t.zone_free("a", 2)
    assert t.can_move(edge(t, "s", "a"), 1)   # next drone enters a at 2


def test_waiting_books_zone() -> None:
    t = build()
    t.reserve_wait("a", 1)
    t.reserve_wait("a", 2)
    assert not t.zone_free("a", 2)
    assert not t.zone_free("a", 3)
    assert not t.can_wait("a", 1)


def test_start_and_end_hold_all_drones() -> None:
    t = build(link_capacity=3)
    for _ in range(3):
        assert t.can_wait("s", 0)
        t.reserve_wait("s", 0)
    for _ in range(3):
        assert t.zone_free("e", 5)
        t.zone_count[("e", 5)] += 1
