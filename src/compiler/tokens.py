from enum import StrEnum, auto

from typing_extensions import override

from compiler.position import Position


class TokenType(StrEnum):
    INTEGER = auto()
    KEYWORD_INTEGER = auto()
    KEYWORD_BOOLEAN = auto()
    KEYWORD_IF = auto()
    KEYWORD_THEN = auto()
    KEYWORD_ELSE = auto()
    KEYWORD_NOT = auto()
    KEYWORD_AND = auto()
    KEYWORD_OR = auto()
    KEYWORD_FUNCTION = auto()
    KEYWORD_PRINT = auto()
    BOOLEAN = auto()
    IDENTIFIER = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    COMMA = auto()
    COLON = auto()
    PLUS = auto()
    MINUS = auto()
    TIMES = auto()
    DIVIDE = auto()
    LESS_THAN = auto()
    EQUAL = auto()
    END_OF_FILE = auto()

    @override
    def __str__(self):
        return self.name.upper()


class Token:
    def __init__(
        self,
        position: Position,
        token_type: TokenType,
        token_value: str | None = None,
    ):
        self.position: Position = position
        self.token_type: TokenType = token_type
        self.token_value: str | None = token_value

    def value(self):
        return self.token_value

    @override
    def __str__(self):
        out = str(self.token_type)
        if self.token_value is not None:
            out += f":{self.token_value}"
        return out

    @override
    def __eq__(self, other: object):
        if isinstance(other, TokenType):
            return self.token_type == other
        if isinstance(other, Token):
            return (
                self.token_type == other.token_type
                and self.token_value == other.token_value
                and self.position == other.position
            )
        raise ValueError("Tokens can only be compared with other tokens or TokenTypes")
