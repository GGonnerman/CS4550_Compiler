from dataclasses import dataclass
from enum import Enum, auto


class IROperation(Enum):
    NEGATE = auto()
    TIMES = auto()
    DIVIDE = auto()
    PLUS = auto()
    MINUS = auto()
    SET_LITERAL = auto()


@dataclass
class IR:
    result: int | str
    arg1: int | str | None
    op: IROperation | None
    arg2: int | str | None
