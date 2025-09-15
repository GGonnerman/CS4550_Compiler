from enum import Enum
from typing import TYPE_CHECKING

from token_agl import Token, TokenType

if TYPE_CHECKING:
    from collections.abc import Iterator


class State(Enum):
    looking = 1
    integer = 2
    string = 3


LOWERCASE_ALPHABET = "abcdefghijklmnopqrstuvwxyz"
UPPERCASE_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHABET = LOWERCASE_ALPHABET + UPPERCASE_ALPHABET
NON_ZERO_INTEGERS = "123456789"
INTEGERS = "0" + NON_ZERO_INTEGERS
IDENTIFIER_CHARACTERS = ALPHABET + INTEGERS + "_"
PUNCTUATION = "(),:"
OPERATORS = "*-/<="
SKIPPABLE = "\t\n "
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
    """One item buffer for reading an item-position sequence"""

    def __init__(self, program: str):
        self.iter: Iterator[str] = iter(program)
        self.pos = None
        self.done = False
        self.value = ""
        self.position = 0
        self._advance()

    def _advance(self):
        try:
            self.item, self.pos = next(self.iter)
        except StopIteration:
            self.done = True

    def peek(self):
        """return current item"""

        if self.done:
            # raise exception
            raise Exception("Cannot peek terminated scanner")

        return self.item

    def get(self):
        """return current item and advance to next"""

        assert not self.done
        item = self.item
        self._advance()
        return item

    def scan_token(self):
        # need checks for all token types
        # skip white space and comments
        # check for end of file
        pass

    def _state0(self, word: str, pos: int):
        if pos >= len(word):
            print("reject")
        else:
            current_char = word[pos]
            if current_char == "0":
                print("reject")
            self.value = ""
            if current_char in ALPHABET:
                self._state1(word, pos + 1)
            elif current_char in NON_ZERO_INTEGERS:
                self._state2(word, pos + 1)
            elif current_char == "(":
                # here we go to a combined "punctuation or whitespace" field
                # which disambiguates
                self._state3(word, pos + 1)
            elif current_char in PUNCTUATION:
                self._state4(word, pos + 1)
            elif current_char in OPERATORS:
                self._state5(word, pos + 1)
            elif current_char in SKIPPABLE:
                self._state6(word, pos + 1)
            else:
                raise Exception("Invalid character")

    def _state1(self, word: str, pos: int):
        if pos >= len(word):
            print("reject")
        else:
            current_char = word[pos]
            self.value += current_char
            if current_char in IDENTIFIER_CHARACTERS:
                return self._state1(word, pos + 1)
            return Token(TokenType.identifier, self.value)
        return None

    def _state2(self, word: str, pos: int):
        pass

    def _state3(self, word: str, pos: int):
        pass

    def _state4(self, word: str, pos: int):
        pass

    def _state5(self, word: str, pos: int):
        pass

    def _state6(self, word: str, pos: int):
        pass
