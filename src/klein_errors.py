class KleinError(Exception):
    pass


class LexicalError(KleinError):
    def __init__(self, position, *args: object) -> None:
        self._position = position
        super().__init__(*args)

    def __str__(self) -> str:
        return f"Klein Lexical Error at position {self._position}: {super().__str__()}"
