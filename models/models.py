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
    zone_type: ZoneType
    role: Role
    color: str | None
    max_drones: int = 1


# FIXME
@dataclass(frozen=True, slots=True)
class Connection():
    zone_a: str
    zone_b: str
    max_links: int = 1
