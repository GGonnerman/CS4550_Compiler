from typing_extensions import override

from compiler.position import Position
from compiler.util import insert_newlines


class KleinError(Exception):
    pass


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
