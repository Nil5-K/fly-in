"""Tests for the time-expanded A* (independent of the plain A*)."""
from pathlib import Path

import pytest

from graph_index import GraphIndex
from heuristic import Heuristic
from models.models import Connection, Graph, Role, Step, Zone, ZoneType
from parser import Parser
from reservation_table import ReservationTable
from time_a_star import TimeAStar

MAPS_DIR = Path(__file__).resolve().parent.parent / "maps"

N, R, B = ZoneType.NORMAL, ZoneType.RESTRICTED, ZoneType.BLOCKED


def make(graph: Graph) -> TimeAStar:
    """Build a TimeAStar with an empty reservation table."""
    index = GraphIndex().build_index(graph)
    return TimeAStar(
        graph, index, Heuristic(graph, index), ReservationTable(graph)
    )


def from_map(map_file: str) -> TimeAStar:
    """Parse a provided map and build a TimeAStar for it."""
    return make(Parser(str(MAPS_DIR / map_file)).parse())


def small(
    types: dict[str, ZoneType],
    links: list[tuple[str, str, int]],
    drones: int = 1,
    zone_cap: int = 1,
) -> TimeAStar:
    """Hand-made graph: first zone is the start, last zone is the end."""
    zones = {
        name: Zone(name, i, 0, Role.NORMAL, kind, max_drones=zone_cap)
        for i, (name, kind) in enumerate(types.items())
    }
    names = list(zones)
    graph = Graph(
        nb_drones=drones,
        zones=zones,
        connections=[Connection(a, b, cap) for a, b, cap in links],
        start=names[0],
        end=names[-1],
    )
    return make(graph)


def arrival(route: list[Step]) -> int:
    """Return the turn in which the route reaches its last zone."""
    last = route[-1]
    assert last.edge is not None
    return last.t + last.edge.cost


def zones_of(route: list[Step]) -> list[str]:
    """Return the zone of each step, in order."""
    return [s.zone for s in route]


def plan(astar: TimeAStar) -> list[Step]:
    """Find a route, book it in the table and return it."""
    route = astar.find_route()
    assert route is not None
    for step in route:
        if step.edge is None:
            astar.table.reserve_wait(step.zone, step.t)
        else:
            astar.table.reserve_move(step.edge, step.t)
    return route


# --- empty table: the result is fixed by the map alone -------------------

@pytest.mark.parametrize("map_file, turns", [
    ("easy/01_linear_path.txt", 3),
    ("easy/02_simple_fork.txt", 3),
    ("easy/03_basic_capacity.txt", 3),
])
def test_single_drone_on_provided_maps(map_file: str, turns: int) -> None:
    route = from_map(map_file).find_route()
    assert route is not None
    assert arrival(route) == turns
    assert all(s.edge is not None for s in route)   # never waits


def test_route_is_connected() -> None:
    astar = from_map("easy/02_simple_fork.txt")
    route = plan(astar)
    assert route[0].zone == astar.graph.start
    assert route[0].t == 0
    for a, b in zip(route, route[1:]):
        assert a.edge is not None
        assert a.edge.target == b.zone
        assert b.t == a.t + a.edge.cost
    last = route[-1]
    assert last.edge is not None
    assert last.edge.target == astar.graph.end


def test_picks_shorter_route() -> None:
    astar = small(
        {"s": N, "a": N, "b": N, "m": N, "e": N},
        [("s", "a", 1), ("a", "b", 1), ("b", "e", 1),
         ("s", "m", 1), ("m", "e", 1)],
    )
    route = astar.find_route()
    assert route is not None
    assert zones_of(route) == ["s", "m"]
    assert arrival(route) == 2


def test_restricted_zone_costs_two_turns() -> None:
    astar = small({"s": N, "r": R, "e": N}, [("s", "r", 1), ("r", "e", 1)])
    route = astar.find_route()
    assert route is not None
    assert [(s.zone, s.t) for s in route] == [("s", 0), ("r", 2)]
    assert arrival(route) == 3


def test_blocked_zone_is_avoided() -> None:
    astar = small(
        {"s": N, "x": B, "a": N, "e": N},
        [("s", "x", 1), ("x", "e", 1), ("s", "a", 1), ("a", "e", 1)],
    )
    route = astar.find_route()
    assert route is not None
    assert "x" not in zones_of(route)


def test_unreachable_end_returns_none() -> None:
    astar = small({"s": N, "a": N, "e": N}, [("s", "a", 1)])
    assert astar.find_route() is None


def test_turn_limit_too_small_returns_none() -> None:
    astar = small({"s": N, "a": N, "e": N}, [("s", "a", 1), ("a", "e", 1)])
    astar.max_turn = 1
    assert astar.find_route() is None


# --- with reservations: later drones must adapt --------------------------

def test_follower_waits_one_turn_on_a_line() -> None:
    astar = small(
        {"s": N, "a": N, "e": N},
        [("s", "a", 1), ("a", "e", 1)],
        drones=2,
    )
    assert arrival(plan(astar)) == 2
    assert arrival(plan(astar)) == 3


def test_follower_waits_in_start_not_in_a_hallway() -> None:
    astar = small(
        {"s": N, "a": N, "e": N},
        [("s", "a", 1), ("a", "e", 1)],
        drones=2,
    )
    plan(astar)
    second = plan(astar)
    assert second[0].zone == "s"
    assert second[0].edge is None     # waits in the start first


def test_link_capacity_one_spaces_drones_out() -> None:
    # zones hold 3, only the link s-e limits: one drone per turn
    astar = small(
        {"s": N, "e": N}, [("s", "e", 1)], drones=3, zone_cap=3
    )
    assert [arrival(plan(astar)) for _ in range(3)] == [1, 2, 3]


def test_link_capacity_two_lets_two_drones_go_together() -> None:
    astar = small(
        {"s": N, "e": N}, [("s", "e", 2)], drones=3, zone_cap=3
    )
    assert [arrival(plan(astar)) for _ in range(3)] == [1, 1, 2]


def test_second_drone_uses_parallel_path() -> None:
    astar = small(
        {"s": N, "a": N, "b": N, "e": N},
        [("s", "a", 1), ("s", "b", 1), ("a", "e", 1), ("b", "e", 1)],
        drones=2,
    )
    first = plan(astar)
    second = plan(astar)
    assert arrival(first) == arrival(second) == 2
    assert zones_of(first)[1:] != zones_of(second)[1:]


def test_waits_instead_of_taking_much_longer_detour() -> None:
    # short way s-a-e (2), long way s-b-c-d-e (4); second drone waits 1
    astar = small(
        {"s": N, "a": N, "b": N, "c": N, "d": N, "e": N},
        [("s", "a", 1), ("a", "e", 1), ("s", "b", 1), ("b", "c", 1),
         ("c", "d", 1), ("d", "e", 1)],
        drones=2,
    )
    assert arrival(plan(astar)) == 2
    assert arrival(plan(astar)) == 3


def test_fork_map_three_drones() -> None:
    astar = from_map("easy/02_simple_fork.txt")
    assert [arrival(plan(astar)) for _ in range(3)] == [3, 4, 5]


@pytest.mark.parametrize("map_file", sorted(
    str(p.relative_to(MAPS_DIR)) for p in MAPS_DIR.glob("*/*.txt")
))
def test_every_drone_of_every_map_gets_a_route(map_file: str) -> None:
    astar = from_map(map_file)
    for _ in range(astar.graph.nb_drones):
        route = plan(astar)
        assert all(
            astar.graph.zones[s.zone].zone_type != B for s in route
        )
