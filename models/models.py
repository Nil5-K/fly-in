from enum import Enum
from dataclasses import dataclass


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Role(Enum):
    START = "start"
    END = "end"
    NORMAL = "normal"


@dataclass(frozen=True, slots=True)
class Zone():
    name: str
    x: int
    y: int
    role: Role
    zone_type: ZoneType = ZoneType.NORMAL
    color: str | None = None
    max_drones: int = 1


@dataclass(frozen=True, slots=True)
class Connection():
    zone_a: str
    zone_b: str
    max_link_capacity: int = 1

    @property
    def key(self) -> frozenset[str]:
        return frozenset((self.zone_a, self.zone_b))

    @property
    def name(self) -> str:
        return f"{self.zone_a}-{self.zone_b}"

    def other(self, zone: str) -> str:
        if zone == self.zone_a:
            return self.zone_b
        if zone == self.zone_b:
            return self.zone_a
        raise ValueError(f"{zone!r} is not part of connection {self.name}")


@dataclass(frozen=True, slots=True)
class Graph():
    nb_drones: int
    zones: dict[str, Zone]
    connections: list[Connection]
    start: str
    end: str
