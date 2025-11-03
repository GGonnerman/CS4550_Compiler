from typing_extensions import override

from compiler.position import Position
from compiler.util import insert_newlines


class KleinError(Exception):
    def format_line_position(self, original_line: str, position: Position) -> str:
        # This method is a bit too complex, but it essentially adds the line number
        # and then spaces for subsequent lines. Then, it prints a carrot indicating
        # the position (in this new wrapped string) where the error occured
        line_indicator_length = (
            len(str(position.get_line_number())) + 1
        )  # +1 accounts for pipe character
        line_with_indicators: list[str] = []
        for idx, line in enumerate(
            insert_newlines(original_line, 80 - line_indicator_length).split("\n"),
        ):
            if idx == 0:
                line_with_indicators.append(f"{position.get_line_number()}|{line}")
            else:
                line_with_indicators.append(f"{' ' * line_indicator_length}{line}")
        display_position = position.get_position()
        for line in line_with_indicators:
            if display_position > (len(line) - 1):
                display_position -= len(line) - 1
                continue
            break

        # TODO: In some cases edge, this is off by one
        display_position += 1  # This account for 0 vs 1 indexing
        return "\n".join(
            [
                "\n".join(line_with_indicators),
                display_position * " " + "^",
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
        position: Position | None = None,
        original_line: str | None = None,
        *args: object,
    ) -> None:
        self._message: str = cause
        self._position: Position | None = position
        self._original_line: str | None = original_line
        super().__init__(*args)

    @override
    def __str__(self) -> str:
        if self._original_line is not None and self._position is not None:
            line_information = (
                f"\n{self.format_line_position(self._original_line, self._position)}"
            )
        else:
            line_information = ""
        return insert_newlines(
            f"Klein Parse Error: {self._position}{line_information}\n{self._message}",
        )


class SemanticError(KleinError):
    def __init__(self, message: str):
        super().__init__()
        self._message: str = message

    @override
    def __str__(self) -> str:
        return insert_newlines(
            f"Klein Semantic Error: {self._message}",
        )
