from models import Zone, Connection, Graph, ZoneType, Role


class ParsingError(Exception):
    """Raised for an invalid map file, with the line number."""
    def __init__(self, line_number: int, msg: str) -> None:
        """Build the error message.

        Args:
            line_number: Line of the problem in the file.
            msg: Description of the problem.
        """
        self.line_number = line_number
        self.msg = msg
        super().__init__(f"line {line_number}: {msg}")


class Parser():
    """Read a map file and build a Graph."""
    def __init__(self, file_path: str) -> None:
        """Store the path of the map file.

        Args:
            file_path: Path of the map file.
        """
        self._file_path = file_path

    @staticmethod
    def _to_int(text: str, line_number: int, key: str) -> int:
        """Convert text to an int.

        Args:
            text: Text to convert.
            line_number: Line, for errors.
            key: Name of the value, for errors.

        Returns:
            The integer value.

        Raises:
            ParsingError: If text is not a number.
        """
        try:
            return int(text)
        except ValueError:
            raise ParsingError(line_number, f"{key}: bad number {text!r}")

    @staticmethod
    def _parse_meta(text: str, line_number: int) -> tuple[str, dict[str, str]]:
        """Split 'name x y [key=value ...]' into core and metadata.

        Args:
            text: The part of the line after the colon.
            line_number: Line, for errors.

        Returns:
            The text before the brackets and a dict of the metadata.

        Raises:
            ParsingError: If the brackets or a pair are malformed.
        """
        if "[" not in text:
            return text.strip(), {}
        if not text.endswith("]"):
            raise ParsingError(line_number, "bad metadata: missing ']'")
        left, _, right = text[:-1].partition("[")
        meta: dict[str, str] = {}
        for r in right.split():
            key, _, value = r.partition("=")
            if not key or not value:
                raise ParsingError(line_number, f"bad metadata {r!r}")
            meta[key] = value
        return left.strip(), meta

    def parse(self) -> Graph:
        """Read the file and check every line.

        Comments start with '#'. nb_drones must come first. Zone names must
        be unique and contain no '-', connections must link known zones
        and may not repeat, and there must be one start and one end hub.

        Returns:
            The Graph described by the file.

        Raises:
            ParsingError: If the file content is invalid.
            OSError: If the file cannot be read.
        """
        nb_drones = 0
        zones: dict[str, Zone] = {}
        connections: list[Connection] = []
        seen: set[frozenset[str]] = set()
        start: str = ""
        end: str = ""

        try:
            with open(self._file_path, encoding="utf-8") as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            raise ParsingError(0, "file is not valid UTF-8 text")

        for n, raw in enumerate(lines, start=1):
            line = raw.split("#")[0].strip()
            if not line:
                continue
            key, _, rest = line.partition(":")
            key = key.strip()
            core, meta = self._parse_meta(rest.strip(), n)

            if nb_drones == 0 and key != "nb_drones":
                raise ParsingError(n, "nb_drones not valid")
            if key == "nb_drones":
                nb_drones = self._to_int(core, n, "nb_drones")
                if nb_drones < 1:
                    raise ParsingError(n, "nb_drones is < 1")
            elif key in ("hub", "start_hub", "end_hub"):
                parts = core.split()
                if len(parts) != 3:
                    raise ParsingError(n, "expected: name x y")
                name = parts[0]
                if "-" in name or name in zones:
                    raise ParsingError(n, f"bad or duplicate name {name!r}")
                try:
                    zone_type = ZoneType(meta.get("zone", "normal"))
                except ValueError:
                    raise ParsingError(n, "bad zone_type")
                max_drones = 1
                if "max_drones" in meta:
                    max_drones = self._to_int(meta["max_drones"],
                                              n, "max_drones")
                    if max_drones < 1:
                        raise ParsingError(n, "max_drones is < 1")
                role = Role.NORMAL
                if key == "start_hub":
                    if start:
                        raise ParsingError(n, "multiple start_hubs")
                    role, start = Role.START, name
                elif key == "end_hub":
                    if end:
                        raise ParsingError(n, "multiple end_hubs")
                    role, end = Role.END, name
                zones[name] = Zone(
                    name=name,
                    x=self._to_int(parts[1], n, "x"),
                    y=self._to_int(parts[2], n, "y"),
                    role=role,
                    zone_type=zone_type,
                    color=meta.get("color"),
                    max_drones=max_drones
                )
            elif key == "connection":
                con_names = core.split("-")
                if len(con_names) != 2:
                    raise ParsingError(n, "expected: zone1-zone2")
                a, b = con_names
                if a not in zones or b not in zones:
                    raise ParsingError(n, "unknown zone in connection")
                link = frozenset((a, b))
                if a == b or link in seen:
                    raise ParsingError(n, "bad connection or duplicate")
                seen.add(link)
                link_capacity = 1
                if "max_link_capacity" in meta:
                    link_capacity = self._to_int(meta["max_link_capacity"],
                                                 n, "max_link_capacity")
                    if link_capacity < 1:
                        raise ParsingError(n, "capacity is < 1")
                connections.append(Connection(a, b, link_capacity))
            else:
                raise ParsingError(n, f"unknown key {key!r}")
        if not start or not end:
            raise ParsingError(len(lines), "missing start_hub or end_hub")
        return Graph(nb_drones, zones, connections, start, end)
