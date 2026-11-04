from dataclasses import dataclass
from enum import Enum


class ZoneType(Enum):
    """Kind of zone: it changes the cost and the access rules."""
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Role(Enum):
    """Position of a zone in the route: start, end or neither."""
    START = "start"
    END = "end"
    NORMAL = "normal"


@dataclass(frozen=True, slots=True)
class Zone():
    """A hub on the map with its position and capacity."""
    name: str
    x: int
    y: int
    role: Role
    zone_type: ZoneType = ZoneType.NORMAL
    color: str | None = None
    max_drones: int = 1


@dataclass(frozen=True, slots=True)
class Connection():
    """A two-way link between two zones."""
    zone_a: str
    zone_b: str
    max_link_capacity: int = 1

    @property
    def key(self) -> frozenset[str]:
        """Return an order-independent id of the link.

        Returns:
            frozenset of the two zone names.
        """
        return frozenset((self.zone_a, self.zone_b))

    @property
    def name(self) -> str:
        """Return the link name as 'zone_a-zone_b'."""
        return f"{self.zone_a}-{self.zone_b}"

    def other(self, zone: str) -> str:
        """Return the zone at the other end of the link.

        Args:
            zone: One end of the connection.

        Returns:
            The name of the opposite end.

        Raises:
            ValueError: If zone is not part of this connection.
        """
        if zone == self.zone_a:
            return self.zone_b
        if zone == self.zone_b:
            return self.zone_a
        raise ValueError(f"{zone!r} is not part of connection {self.name}")


@dataclass(frozen=True, slots=True)
class Graph():
    """The parsed map: drones, zones, connections, start and end."""
    nb_drones: int
    zones: dict[str, Zone]
    connections: list[Connection]
    start: str
    end: str


@dataclass(frozen=True, slots=True)
class Edge():
    """A directed move over a connection towards a target zone."""
    connection: Connection
    target: str
    cost: int = 1


@dataclass(frozen=True, slots=True)
class Step():
    """One action of a drone: wait in a zone or take an edge at turn t."""
    zone: str
    t: int
    edge: Edge | None = None
