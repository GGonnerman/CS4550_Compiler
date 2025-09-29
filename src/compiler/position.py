from typing import SupportsIndex

from typing_extensions import override


class Position(SupportsIndex):
    def __init__(
        self,
        line_number: int = 0,
        position: int = 0,
        absolute_position: int = 0,
    ):
        self._line_number: int = line_number
        self._position: int = position
        self._absolute_position: int = absolute_position

    def copy(self):
        return Position(
            self._line_number,
            self._position,
            self._absolute_position,
        )

    def load(self, position: "Position"):
        self._line_number = position.get_line_number()
        self._position = position.get_position()
        self._absolute_position = position.get_absolute_position()

    def __iadd__(self, other: object):
        if not isinstance(other, int):
            raise TypeError("Cannot add non-integer to position")
        self._absolute_position += other
        self._position += other
        return self

    @override
    def __index__(self) -> int:
        return self._absolute_position

    @override
    def __eq__(self, other: object):
        if isinstance(other, Position):
            return (
                self._absolute_position == other.get_absolute_position()
                and self._line_number == other.get_line_number()
                and self._position == other.get_position()
            )
        if isinstance(other, int):
            return self._absolute_position == other
        raise ValueError("Positions can only be compared with other positions or ints")

    def __ge__(self, other: int):
        return self._absolute_position >= other

    def add_newline(self):
        self._position = 0
        self._line_number += 1

    def get_line_number(self):
        return self._line_number

    def get_position(self):
        return self._position

    def get_absolute_position(self):
        return self._absolute_position

    @override
    def __str__(self):
        return f"Line {self._line_number} Position {self._position}"
