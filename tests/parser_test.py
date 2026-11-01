"""Tests for the map parser."""
from pathlib import Path

import pytest

from models import Role, ZoneType
from parser import Parser, ParsingError

MAPS_DIR = Path(__file__).resolve().parent.parent / "maps"

# smallest valid map; error cases modify or extend it
BASE = [
    "nb_drones: 2",
    "start_hub: s 0 0",
    "end_hub: e 1 0",
    "connection: s-e",
]


def parse(tmp_path: Path, lines: list[str]):
    """Write ``lines`` to a temp map file and parse it."""
    path = tmp_path / "map.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return Parser(str(path)).parse()


# ---------- valid input ----------

def test_valid_minimal_map(tmp_path: Path) -> None:
    graph = parse(tmp_path, BASE)
    assert graph.nb_drones == 2
    assert graph.start == "s"
    assert graph.end == "e"
    assert graph.zones["s"].role is Role.START
    assert graph.zones["e"].role is Role.END
    assert len(graph.connections) == 1


def test_metadata_and_defaults(tmp_path: Path) -> None:
    graph = parse(tmp_path, BASE + [
        "hub: h 2 -1 [zone=restricted color=red max_drones=3]",
        "hub: plain 3 3",
        "connection: s-h [max_link_capacity=2]",
    ])
    h = graph.zones["h"]
    assert (h.x, h.y) == (2, -1)
    assert h.zone_type is ZoneType.RESTRICTED
    assert h.color == "red"
    assert h.max_drones == 3
    plain = graph.zones["plain"]
    assert plain.zone_type is ZoneType.NORMAL
    assert plain.color is None
    assert plain.max_drones == 1
    caps = {c.name: c.max_link_capacity for c in graph.connections}
    assert caps == {"s-e": 1, "s-h": 2}


def test_comments_and_blank_lines_ignored(tmp_path: Path) -> None:
    graph = parse(tmp_path, [
        "# header comment",
        "",
        "nb_drones: 2  # trailing comment",
        "start_hub: s 0 0",
        "end_hub: e 1 0",
        "   ",
        "connection: s-e",
    ])
    assert graph.nb_drones == 2
    assert len(graph.connections) == 1


@pytest.mark.parametrize("map_file", sorted(MAPS_DIR.glob("*/*.txt")),
                         ids=lambda p: p.name)
def test_provided_maps_parse(map_file: Path) -> None:
    graph = Parser(str(map_file)).parse()
    assert graph.nb_drones > 0
    assert graph.start in graph.zones
    assert graph.end in graph.zones
    assert graph.connections


# ---------- error cases: (lines, expected line number, message part) ----

ERROR_CASES = {
    "duplicate_reversed_connection": (
        BASE + ["connection: e-s"], 5, "duplicate"),
    "duplicate_same_connection": (
        BASE + ["connection: s-e"], 5, "duplicate"),
    "unknown_zone": (
        BASE + ["connection: s-x"], 5, "unknown zone"),
    "bad_zone_type": (
        BASE + ["hub: h 1 1 [zone=foo]"], 5, "zone_type"),
    "max_drones_zero": (
        BASE + ["hub: h 1 1 [max_drones=0]"], 5, "max_drones"),
    "max_drones_not_a_number": (
        BASE + ["hub: h 1 1 [max_drones=abc]"], 5, "max_drones"),
    "link_capacity_zero": (
        BASE + ["hub: h 1 1", "connection: s-h [max_link_capacity=0]"],
        6, "capacity"),
    "missing_closing_bracket": (
        BASE + ["hub: h 1 1 [zone=normal"], 5, "missing ']'"),
    "metadata_without_value": (
        BASE + ["hub: h 1 1 [zone=]"], 5, "metadata"),
    "two_starts": (
        BASE + ["start_hub: s2 2 2"], 5, "multiple start_hubs"),
    "two_ends": (
        BASE + ["end_hub: e2 2 2"], 5, "multiple end_hubs"),
    "no_end": (
        ["nb_drones: 2", "start_hub: s 0 0"], 2, "missing"),
    "no_start": (
        ["nb_drones: 2", "end_hub: e 1 0"], 2, "missing"),
    "dash_in_name": (
        BASE + ["hub: a-b 1 1"], 5, "bad or duplicate name"),
    "duplicate_zone_name": (
        BASE + ["hub: s 5 5"], 5, "bad or duplicate name"),
    "bad_coordinate": (
        BASE + ["hub: h x 1"], 5, "bad number"),
    "missing_coordinate": (
        BASE + ["hub: h 1"], 5, "expected: name x y"),
    "nb_drones_zero": (
        ["nb_drones: 0"] + BASE[1:], 1, "nb_drones"),
    "nb_drones_not_first": (
        BASE[1:] + ["nb_drones: 2"], 1, "nb_drones"),
    "unknown_key": (
        BASE + ["foo: bar"], 5, "unknown key"),
    "self_loop": (
        BASE + ["connection: s-s"], 5, "bad connection"),
}


@pytest.mark.parametrize("lines, line_no, fragment",
                         ERROR_CASES.values(), ids=ERROR_CASES.keys())
def test_parse_errors(tmp_path: Path, lines: list[str],
                      line_no: int, fragment: str) -> None:
    with pytest.raises(ParsingError) as exc:
        parse(tmp_path, lines)
    assert exc.value.line_number == line_no
    assert fragment in exc.value.msg


def test_missing_file() -> None:
    with pytest.raises(OSError):
        Parser("does/not/exist.txt").parse()
