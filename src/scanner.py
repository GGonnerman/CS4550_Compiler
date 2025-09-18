from klein_errors import LexicalError
from token_agl import Token, TokenType

ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
NON_ZERO_INTEGERS = "123456789"
INTEGERS = "0" + NON_ZERO_INTEGERS
IDENTIFIER_CHARACTERS = ALPHABET + INTEGERS + "_"
PUNCTUATION = "(),:"
OPERATORS = "+-*/<="
SKIPPABLE = "\t\n ("
DELIMITERS = PUNCTUATION + OPERATORS + SKIPPABLE
KEYWORDS = [
    "integer",
    "boolean",
    "if",
    "then",
    "else",
    "not",
    "and",
    "or",
    "function",
]
PRIMATIVE_IDENTIFIERS = ["print"]
BOOLEAN_LITERALS = ["true", "false"]


class Scanner:
    def __init__(self, program: str):
        self.program: str = program
        self.has_terminated: bool = False
        self.position: int = 0
        self.working_position: int = 0
        self.accum: str = ""

    def __iter__(self):
        while self.has_next():
            yield self.next()

    def next(self):
        return self._next(update_position=True)

    def peek(self):
        return self._next(update_position=False)

    def _next(self, *, update_position: bool = True):
        if self.has_terminated:
            raise Exception("Cannot get more tokens after scanner has terminated")

        token: Token | None = None
        while token is None:
            self.position = self.working_position
            token = self._stage0()

        if update_position:
            self.position = self.working_position
            self.has_terminated = token.is_a(TokenType.END_OF_FILE)
        else:
            self.working_position = self.position

        return token

    def _stage0(self):
        if self.working_position >= len(self.program):
            return Token(TokenType.END_OF_FILE)
        self.accum = ""
        char = self.program[self.working_position]
        if char in ALPHABET:
            self.accum += char
            self.working_position += 1
            return self._stage1()
        if char in "0":
            self.accum += char
            self.working_position += 1
            return self._stage2()
        if char in NON_ZERO_INTEGERS:
            self.accum += char
            self.working_position += 1
            return self._stage3()
        if char in OPERATORS:
            self.accum += char
            self.working_position += 1
            return self._stage4()
        if char in "(":
            self.accum += char
            self.working_position += 1
            return self._stage5()
        if char in SKIPPABLE:
            self.accum += char
            self.working_position += 1
            return self._stage9()
        if char in PUNCTUATION:
            self.accum += char
            self.working_position += 1
            return self._stage10()
        raise LexicalError(f'Unknown character "{char}" when looking for next token.')

    def _categorize_identifier(self, identifier: str) -> Token:
        max_identifier_length = 256
        if len(identifier) > max_identifier_length:
            raise LexicalError("Identifiers cannot be longer than 256 characters")
        if identifier in BOOLEAN_LITERALS:
            return Token(TokenType.BOOLEAN, self.accum)
        if identifier in PRIMATIVE_IDENTIFIERS:
            return Token(TokenType.PRIMITIVE_IDENTIFIER, self.accum)
        if identifier in KEYWORDS:
            return Token(TokenType.KEYWORD, self.accum)
        return Token(TokenType.IDENTIFIER, self.accum)

    def _stage1(self) -> Token:
        if self.working_position >= len(self.program):
            return self._categorize_identifier(self.accum)
        char = self.program[self.working_position]
        if char in IDENTIFIER_CHARACTERS:
            self.accum += char
            self.working_position += 1
            return self._stage1()
        if char in DELIMITERS:
            return self._categorize_identifier(self.accum)
        raise LexicalError(
            self.working_position,
            f'Invalid character "{char}" in identifier. Only alphanumeric characters and underscores allowed.',
        )

    def _stage2(self) -> Token:
        if self.working_position >= len(self.program):
            return Token(TokenType.INTEGER, self.accum)
        char = self.program[self.working_position]
        if char in DELIMITERS:
            return Token(TokenType.INTEGER, self.accum)
        if char in INTEGERS:
            raise LexicalError("Integer cannot start with leading 0")
        raise LexicalError("Invalid char in integer")

    def _stage3(self) -> Token:
        if self.working_position >= len(self.program):
            return Token(TokenType.INTEGER, self.accum)
        char = self.program[self.working_position]
        if char in INTEGERS:
            self.accum += char
            self.working_position += 1
            return self._stage3()
        if char in DELIMITERS:
            return Token(TokenType.INTEGER, self.accum)
        raise LexicalError("Invalid char in integer")

    def _categorize_opterator(self, operator: str):
        if operator == "+":
            return Token(TokenType.PLUS)
        if operator == "-":
            return Token(TokenType.MINUS)
        if operator == "*":
            return Token(TokenType.TIMES)
        if operator == "/":
            return Token(TokenType.DIVIDE)
        if operator == "<":
            return Token(TokenType.LESS_THAN)
        if operator == "=":
            return Token(TokenType.EQUAL)
        raise LexicalError(f"Unable to categorize identifier: '{operator}'")

    def _stage4(self) -> Token:
        return self._categorize_opterator(self.accum)

    def _stage5(self) -> Token | None:
        if self.working_position >= len(self.program):
            return self._categorize_punctuation(self.accum)
        char = self.program[self.working_position]
        if char in "*":
            self.accum += char
            self.working_position += 1
            return self._stage6()
        return self._categorize_punctuation(self.accum)

    def _stage6(self) -> Token | None:
        if self.working_position >= len(self.program):
            raise LexicalError("All comments must be terminated before program ends")
        char = self.program[self.working_position]
        self.accum += char
        self.working_position += 1
        if char in "*":
            return self._stage7()
        return self._stage6()

    def _stage7(self) -> Token | None:
        if self.working_position >= len(self.program):
            raise LexicalError("All comments must be terminated before program ends")
        char = self.program[self.working_position]
        self.accum += char
        self.working_position += 1
        if char in ")":
            return self._stage8()
        return self._stage6()

    def _stage8(self) -> None:
        return

    def _stage9(self) -> None:
        return
        # Don't return anything; this is whitespace which is ignored
        # In theory could return token with type whitespace, but I don't
        # think whitespace is supposed to be a token.

    def _categorize_punctuation(self, punctuation: str):
        if punctuation == "(":
            return Token(TokenType.LEFT_PAREN)
        if punctuation == ")":
            return Token(TokenType.RIGHT_PAREN)
        if punctuation == ",":
            return Token(TokenType.COMMA)
        if punctuation == ":":
            return Token(TokenType.COLON)
        raise LexicalError(f"Unable to categorize identifier: '{punctuation}")

    def _stage10(self) -> Token:
        return self._categorize_punctuation(self.accum)

    def has_next(self) -> bool:
        return not self.has_terminated
