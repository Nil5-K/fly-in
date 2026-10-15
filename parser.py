class ParsingError(Exception):
    _line_number: int
    _msg: str

    def __init__(self, line_number: int, msg: str) -> None:
        self._line_number = line_number
        self._msg = msg
        super().__init__(msg)


# FIXME
class Parser():
    pass
