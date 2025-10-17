from compiler.klein_errors import KleinError, LexicalError
from compiler.position import Position
from compiler.tokens import Token, TokenType

ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
NON_ZERO_INTEGERS = "123456789"
INTEGERS = "0" + NON_ZERO_INTEGERS
IDENTIFIER_CHARACTERS = ALPHABET + INTEGERS + "_"
PUNCTUATION = "(),:"
OPERATORS = "+-*/<="
SKIPPABLE = "\t\n\r ("
DELIMITERS = PUNCTUATION + OPERATORS + SKIPPABLE
KEYWORDS: dict[str, TokenType] = {
    "integer": TokenType.KEYWORD_INTEGER,
    "boolean": TokenType.KEYWORD_BOOLEAN,
    "if": TokenType.KEYWORD_IF,
    "then": TokenType.KEYWORD_THEN,
    "else": TokenType.KEYWORD_ELSE,
    "not": TokenType.KEYWORD_NOT,
    "and": TokenType.KEYWORD_AND,
    "or": TokenType.KEYWORD_OR,
    "function": TokenType.KEYWORD_FUNCTION,
    "print": TokenType.KEYWORD_PRINT,
}
BOOLEANS: set[str] = {"true", "false"}

TOKEN_TO_DISPLAY_CHAR: dict[TokenType, str] = {
    TokenType.LEFT_PAREN: "(",
    TokenType.RIGHT_PAREN: ")",
    TokenType.COMMA: ",",
    TokenType.COLON: ":",
    TokenType.PLUS: "+",
    TokenType.MINUS: "-",
    TokenType.TIMES: "*",
    TokenType.DIVIDE: "/",
    TokenType.LESS_THAN: "<",
    TokenType.EQUAL: "=",
}

TOKEN_TO_DISPLAY_CHAR.update(
    [(v, k) for k, v in KEYWORDS.items()],
)


def tokentype_to_str(token_type: TokenType) -> str:
    if token_type in TOKEN_TO_DISPLAY_CHAR:
        return '"' + TOKEN_TO_DISPLAY_CHAR[token_type] + '"'
    return str(token_type)


class Scanner:
    def __init__(self, program: str):
        self.program: str = program
        self.has_terminated: bool = False
        self.position: Position = Position()
        self.working_position: Position = Position()
        self.accum: str = ""

    def get_line(self, idx: int):
        lines: list[str] = self.program.split("\n")
        if idx < 0 or idx >= len(lines):
            raise IndexError(f"Cannot access line number {idx}: outside of program")
        return lines[idx]

    def __iter__(self):
        while self.has_next():
            yield self.next()

    def next(self):
        return self._next(update_position=True)

    def peek(self):
        return self._next(update_position=False)

    def _next(self, *, update_position: bool = True):
        if self.has_terminated:
            raise KleinError("Cannot call next on a terminated scanner")

        token: Token | None = None
        while token is None:
            self.position.load(self.working_position)
            token = self._stage0()

        if update_position:
            self.position.load(self.working_position)
            self.has_terminated = token == TokenType.END_OF_FILE
        else:
            self.working_position.load(self.position)

        return token

    def _stage0(self):
        if self.working_position >= len(self.program):
            return Token(self.position.copy(), TokenType.END_OF_FILE)
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
        raise LexicalError(
            f'Illegal character "{char}" when looking for next token.',
            self.working_position,
        )

    def _categorize_identifier(self, identifier: str) -> Token:
        max_identifier_length = 256
        if len(identifier) > max_identifier_length:
            raise LexicalError(
                "Identifiers cannot be longer than 256 characters",
                self.working_position,
            )
        if identifier in KEYWORDS:
            token_type = KEYWORDS[identifier]
            return Token(self.position.copy(), token_type)
        if identifier in BOOLEANS:
            return Token(self.position.copy(), TokenType.BOOLEAN, self.accum)
        return Token(self.position.copy(), TokenType.IDENTIFIER, self.accum)

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
        debug_character = char
        if not char.isprintable():
            debug_character = f"utf8:{ord(char)}"

        raise LexicalError(
            f'Invalid character "{debug_character}" in identifier. Only alphanumeric characters and underscores allowed.',
            self.working_position,
        )

    def _validate_integer(self, value: str) -> Token:
        min_integer_incl = 0
        max_integer_incl = (2**31) - 1
        try:
            numeric_value = int(value)
        except Exception:
            raise LexicalError(  # noqa: B904
                f'Encountered illegal integer "{value}"',
                self.working_position,
            )
        if numeric_value < min_integer_incl or numeric_value > max_integer_incl:
            raise LexicalError(
                f"Integer literal must be bounded between {min_integer_incl} (incl) and {max_integer_incl} (incl).",
                self.working_position,
            )
        return Token(self.position.copy(), TokenType.INTEGER, self.accum)

    def _stage2(self) -> Token:
        if self.working_position >= len(self.program):
            return self._validate_integer(self.accum)
        char = self.program[self.working_position]
        if char in DELIMITERS:
            return Token(self.position.copy(), TokenType.INTEGER, self.accum)
        if char in INTEGERS:
            raise LexicalError(
                "Integer cannot start with leading 0",
                self.working_position,
            )
        raise LexicalError(
            f'Invalid character "{char}" in integer',
            self.working_position,
        )

    def _stage3(self) -> Token:
        if self.working_position >= len(self.program):
            return self._validate_integer(self.accum)
        char = self.program[self.working_position]
        if char in INTEGERS:
            self.accum += char
            self.working_position += 1
            return self._stage3()
        if char in DELIMITERS:
            return self._validate_integer(self.accum)
        raise LexicalError(
            f'Invalid character "{char}" in integer',
            self.working_position,
        )

    def _categorize_operator(self, operator: str):
        if operator == "+":
            return Token(self.position.copy(), TokenType.PLUS)
        if operator == "-":
            return Token(self.position.copy(), TokenType.MINUS)
        if operator == "*":
            return Token(self.position.copy(), TokenType.TIMES)
        if operator == "/":
            return Token(self.position.copy(), TokenType.DIVIDE)
        if operator == "<":
            return Token(self.position.copy(), TokenType.LESS_THAN)
        if operator == "=":
            return Token(self.position.copy(), TokenType.EQUAL)
        raise LexicalError(
            f'Unable to categorize operator: "{operator}"',
            self.working_position,
        )

    def _stage4(self) -> Token:
        return self._categorize_operator(self.accum)

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
        # Inside of a comment block, in order to avoid crazy recursion depth, we
        # walk through the entire block in one function to avoid crazy recursion depth
        while True:
            if self.working_position >= len(self.program):
                raise LexicalError(
                    "All comments must be terminated before program ends",
                    self.working_position,
                )

            char = self.program[self.working_position]
            self.accum += char
            self.working_position += 1
            if char == "\n":
                self.working_position.add_newline()
            if char in "*":
                return self._stage7()

    def _stage7(self) -> Token | None:
        if self.working_position >= len(self.program):
            raise LexicalError(
                "All comments must be terminated before program ends",
                self.working_position,
            )
        char = self.program[self.working_position]
        self.accum += char
        self.working_position += 1
        if char == "\n":
            self.working_position.add_newline()
        if char in ")":
            return self._stage8()
        return self._stage6()

    def _stage8(self) -> None:
        return

    def _stage9(self) -> None:
        if self.accum == "\n":
            self.working_position.add_newline()
        # Don't return anything; this is whitespace which is ignored
        # In theory could return token with type whitespace, but I don't
        # think whitespace is supposed to be a token.

    def _categorize_punctuation(self, punctuation: str):
        if punctuation == "(":
            return Token(self.position.copy(), TokenType.LEFT_PAREN)
        if punctuation == ")":
            return Token(self.position.copy(), TokenType.RIGHT_PAREN)
        if punctuation == ",":
            return Token(self.position.copy(), TokenType.COMMA)
        if punctuation == ":":
            return Token(self.position.copy(), TokenType.COLON)
        raise LexicalError(
            f'Unable to categorize punctuation: "{punctuation}"',
            self.working_position,
        )

    def _stage10(self) -> Token:
        return self._categorize_punctuation(self.accum)

    def has_next(self) -> bool:
        return not self.has_terminated
