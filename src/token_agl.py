from enum import IntEnum

from typing_extensions import override


class TokenType(IntEnum):
    int_token = 0
    identifier = 1
    keyword = 2
    boolean = 3
    primitive_identifier = 4
    punctuation = 5
    operator = 6
    eof = 7


class Token:
    def __init__(self, token_type: TokenType, token_value: str | None = None):
        self.token_type: TokenType = token_type
        self.token_value: str | None = token_value

    def is_integer(self):
        return self.token_type == TokenType.int_token

    def is_identifier(self):
        return self.token_type == TokenType.identifier

    def is_keyword(self):
        return self.token_type == TokenType.keyword

    def is_boolean(self):
        return self.token_type == TokenType.boolean

    def is_primitive_identifier(self):
        return self.token_type == TokenType.primitive_identifier

    def is_punctuation(self):
        return self.token_type == TokenType.punctuation

    def is_operator(self):
        return self.token_type == TokenType.operator

    def is_eof(self):
        return self.token_type == TokenType.eof

    def value(self):
        return self.token_value

    @override
    def __repr__(self):
        if self.is_integer():
            return f"integer = {self.token_value}"
        if self.is_identifier():
            return f"identifier = {self.token_value}"
        if self.is_keyword():
            return f"keyword = {self.token_value}"
        if self.is_boolean():
            return f"boolean = {self.token_value}"
        if self.is_primitive_identifier():
            return f"primitive = {self.token_value}"
        if self.is_punctuation():
            return f"punctuation = {self.token_value}"
        if self.is_operator():
            return f"operator = {self.token_value}"
        if self.is_eof():
            return "eof"
        raise ValueError(
            f"Unknown token type {self.token_type} with value {self.token_value}",
        )
