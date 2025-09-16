from token_agl import Token, TokenType

ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
NON_ZERO_INTEGERS = "123456789"
INTEGERS = "0" + NON_ZERO_INTEGERS
IDENTIFIER_CHARACTERS = ALPHABET + INTEGERS + "_"
PUNCTUATION = "(),:"
OPERATORS = "+-*/<="
SKIPPABLE = "\t\n ("
DELIMITERS = PUNCTUATION + OPERATORS + SKIPPABLE + "_"
KEYWORDS = [
    "integer",
    "string",
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
            self.has_terminated = token.is_eof()
        else:
            self.working_position = self.position

        return token

    def _stage0(self):
        if self.working_position >= len(self.program):
            return Token(TokenType.eof)
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
        raise Exception(f'Unknown char: "{char}"')

    def _categorize_identifier(self, identifier: str) -> Token:
        if identifier in BOOLEAN_LITERALS:
            return Token(TokenType.boolean, self.accum)
        if identifier in PRIMATIVE_IDENTIFIERS:
            return Token(TokenType.primitive_identifier, self.accum)
        if identifier in KEYWORDS:
            return Token(TokenType.keyword, self.accum)
        return Token(TokenType.identifier, self.accum)

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
        raise Exception(f"Invalid char in identifier '{char}'")

    def _stage2(self) -> Token:
        if self.working_position >= len(self.program):
            return Token(TokenType.int_token, self.accum)
        char = self.program[self.working_position]
        if char in DELIMITERS:
            return Token(TokenType.int_token, self.accum)
        if char in INTEGERS:
            raise Exception("Integer cannot start with leading 0")
        raise Exception("Invalid char in integer")

    def _stage3(self) -> Token:
        if self.working_position >= len(self.program):
            return Token(TokenType.int_token, self.accum)
        char = self.program[self.working_position]
        if char in INTEGERS:
            self.accum += char
            self.working_position += 1
            return self._stage3()
        if char in DELIMITERS:
            return Token(TokenType.int_token, self.accum)
        raise Exception("Invalid char in integer")

    def _stage4(self) -> Token:
        return Token(TokenType.operator, self.accum)

    def _stage5(self) -> Token | None:
        if self.working_position >= len(self.program):
            return Token(TokenType.punctuation, self.accum)
        char = self.program[self.working_position]
        if char in "*":
            self.accum += char
            self.working_position += 1
            return self._stage6()
        return Token(TokenType.punctuation, self.accum)

    def _stage6(self) -> Token | None:
        if self.working_position >= len(self.program):
            raise Exception("All comments must be terminated before program ends")
        char = self.program[self.working_position]
        self.accum += char
        self.working_position += 1
        if char in "*":
            return self._stage7()
        return self._stage6()

    def _stage7(self) -> Token | None:
        if self.working_position >= len(self.program):
            raise Exception("All comments must be terminated before program ends")
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

    def _stage10(self) -> Token:
        return Token(TokenType.punctuation, self.accum)

    def has_next(self) -> bool:
        return not self.has_terminated
