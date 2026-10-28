"""Tests for the backward-Dijkstra heuristic."""
from pathlib import Path

import pytest

from graph_index import GraphIndex
from heuristic import Heuristic
from models.models import Connection, Graph, Role, Zone, ZoneType
from parser import Parser

MAPS_DIR = Path(__file__).resolve().parent.parent / "maps"


def build(
    types: dict[str, ZoneType], links: list[tuple[str, str]]
) -> Heuristic:
    zones = {
        name: Zone(name, i, 0, Role.NORMAL, zone_type)
        for i, (name, zone_type) in enumerate(types.items())
    }
    names = list(zones)
    graph = Graph(
        nb_drones=1,
        zones=zones,
        connections=[Connection(a, b) for a, b in links],
        start=names[0],
        end=names[-1],
    )
    return Heuristic(graph, GraphIndex().build_index(graph))


N, R, B = ZoneType.NORMAL, ZoneType.RESTRICTED, ZoneType.BLOCKED


def test_goal_is_zero() -> None:
    h = build({"s": N, "e": N}, [("s", "e")])
    assert h.h("e") == 0


def test_linear_path() -> None:
    h = build({"a": N, "b": N, "c": N, "e": N},
              [("a", "b"), ("b", "c"), ("c", "e")])
    assert [h.h(z) for z in "abce"] == [3, 2, 1, 0]


def test_restricted_costs_two_when_entered() -> None:
    # a -> r -> e : entering r costs 2, entering e costs 1
    h = build({"a": N, "r": R, "e": N}, [("a", "r"), ("r", "e")])
    assert h.h("r") == 1
    assert h.h("a") == 3


def test_restricted_goal_costs_two() -> None:
    h = build({"a": N, "e": R}, [("a", "e")])
    assert h.h("a") == 2


def test_picks_cheaper_route() -> None:
    # via r: 2 + 1 = 3, via m: 1 + 1 = 2
    h = build(
        {"a": N, "r": R, "m": N, "e": N},
        [("a", "r"), ("r", "e"), ("a", "m"), ("m", "e")],
    )
    assert h.h("a") == 2  # via m


def test_unreachable_is_none() -> None:
    h = build({"a": N, "b": N, "e": N}, [("a", "b")])
    assert h.h("a") is None
    assert h.h("b") is None


def test_blocked_zone_cuts_path() -> None:
    h = build({"a": N, "x": B, "e": N}, [("a", "x"), ("x", "e")])
    assert h.h("a") is None
    assert h.h("x") is None


def test_unknown_zone_is_none() -> None:
    h = build({"s": N, "e": N}, [("s", "e")])
    assert h.h("nope") is None


@pytest.mark.parametrize("map_file", sorted(MAPS_DIR.rglob("*.txt")),
                         ids=lambda p: p.name)
def test_start_reachable_on_all_maps(map_file: Path) -> None:
    graph = Parser(str(map_file)).parse()
    h = Heuristic(graph, GraphIndex().build_index(graph))
    assert h.h(graph.end) == 0
    assert h.h(graph.start) is not None
