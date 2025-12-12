from dataclasses import dataclass
from enum import Enum, auto


class IROperation(Enum):
    TIMES = auto()
    DIVIDE = auto()
    PLUS = auto()
    MINUS = auto()
    EQUALS = auto()
    LESS_THAN = auto()
    NOT = auto()
    UNARY_MINUS = auto()
    SET_LITERAL = auto()
    COPY = auto()

    PARAM = auto()
    CALL = auto()

    LABEL = auto()
    IF = auto()
    IF_NOT = auto()
    GOTO = auto()


class LoopTrack(Enum):
    ENTER = auto()
    ELSE = auto()
    EXIT = auto()


@dataclass
class IR:
    result: int | str
    arg1: int | str | None
    op: IROperation | None
    arg2: LoopTrack | int | str | None

    def __str__(self) -> str:
        return f"IR(result={self.result}, arg1={self.arg1}, op={self.op.name if self.op else 'None'}, arg2={self.arg2})"
