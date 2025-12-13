from dataclasses import dataclass
from enum import Enum, StrEnum, auto

from typing_extensions import override

# This files contains
# - IROperations used by the intermediate representation (3AC)
# - Loop Status for tracking enter/exiting contexts
#   - Used for the register allocation algorithm
# - IR class which represents a line of 3AC


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
    STORE_LITERAL = auto()
    COPY = auto()

    PARAM = auto()
    CALL = auto()

    LABEL = auto()
    IF = auto()
    IF_NOT = auto()
    GOTO = auto()


class LoopStatus(StrEnum):
    ENTER = auto()
    ELSE = auto()
    EXIT = auto()


@dataclass
class IR:
    result: int | str
    arg1: int | str | None
    op: IROperation | None
    arg2: LoopStatus | int | str | None

    @override
    def __str__(self) -> str:
        return f"IR(result={self.result}, arg1={self.arg1}, op={self.op.name if self.op else 'None'}, arg2={self.arg2})"
