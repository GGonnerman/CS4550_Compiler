from enum import IntEnum, auto

from typing_extensions import override

from compiler.position import Position


class TokenType(IntEnum):
    INTEGER = auto()
    IDENTIFIER = auto()
    KEYWORD = auto()
    BOOLEAN = auto()
    PRIMITIVE_IDENTIFIER = auto()
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

    def is_a(self, token_type: TokenType) -> bool:
        return self.token_type == token_type

    def is_keyword(self):
        return self.token_type in [
            TokenType.KEYWORD,
            TokenType.BOOLEAN,
            TokenType.PRIMITIVE_IDENTIFIER,
        ]

    def is_punctuation(self):
        return self.token_type in [
            TokenType.LEFT_PAREN,
            TokenType.RIGHT_PAREN,
            TokenType.COMMA,
            TokenType.COLON,
        ]

    def is_operator(self):
        return self.token_type in [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.TIMES,
            TokenType.DIVIDE,
            TokenType.LESS_THAN,
            TokenType.EQUAL,
        ]

    def value(self):
        return self.token_value

    @override
    def __repr__(self):
        display = self.token_type.name.lower()
        if self.token_value is not None:
            # Just makes sure the tabs all line up nicely
            display += " " * (20 - len(display))
            display += f"\t{self.value()}"
        return display

    @override
    def __eq__(self, other: object):
        if not isinstance(other, Token):
            return False
        return (
            self.token_type == other.token_type
            and self.token_value == other.token_value
        )
