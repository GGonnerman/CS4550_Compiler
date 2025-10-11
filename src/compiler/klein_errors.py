from typing_extensions import override

from compiler.position import Position
from compiler.util import insert_newlines


class KleinError(Exception):
    def format_line_position(self, line: str, position: Position) -> str:
        line_indicator_length = len(str(position.get_line_number()))
        return "\n".join(
            [
                f"{position.get_line_number()}|{line}",
                (position.get_position() - 1 + line_indicator_length + 1) * " " + "^",
            ],
        )


class LexicalError(KleinError):
    def __init__(
        self,
        cause: str,
        position: Position,
        *args: object,
    ) -> None:
        self._position: Position | None = position
        self._message: str = cause
        super().__init__(*args)

    @override
    def __str__(self) -> str:
        return insert_newlines(
            f"Klein Lexical Error at {self._position}: {self._message}",
        )


class ParseError(KleinError):
    def __init__(
        self,
        cause: str,
        position: Position,
        original_line: str,
        *args: object,
    ) -> None:
        self._message: str = cause
        self._position: Position = position
        self._original_line: str = original_line
        super().__init__(*args)

    @override
    def __str__(self) -> str:
        return insert_newlines(
            f"Klein Parse Error: {self._position}\n{self.format_line_position(self._original_line, self._position)}\n{self._message}",
        )
