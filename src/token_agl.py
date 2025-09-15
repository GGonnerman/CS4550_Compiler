from enum import IntEnum, auto


class TokenType(IntEnum):
    TERMINATOR = auto()
    PUNCTUATION = auto()
    OPERATOR = auto()
    IDENTIFIER = auto()
    INTEGER = auto()
    KEYWORD = auto()
    BOOLEAN = auto()
    PRIMITIVE_IDENTIFIER = auto()


class Token:
    def __init__(self, token_type: TokenType, token_value: int | None = None):
        self.token_type: TokenType = token_type
        self.token_value: int | None = token_value

    # Add "is" commands

    def value(self):
        return self.token_value

    # Add repr command
