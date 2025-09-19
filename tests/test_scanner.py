import pytest

from compiler.klein_errors import KleinError, LexicalError
from compiler.scanner import Scanner
from compiler.token_agl import Token, TokenType


def test_scan_end_of_file():
    s = Scanner("")
    assert s.has_next(), "Empty file should have next input (EOF char)"
    assert s.next().is_a(TokenType.END_OF_FILE), (
        "An empty file should only contain the end of file token"
    )


def test_scan_after_termination_raises():
    s = Scanner("")
    _ = s.next()
    with pytest.raises(KleinError) as excinfo:
        _ = s.next()
    assert str(excinfo.value) == "Cannot call next on a terminated scanner"


def test_next_should_move_ahead():
    s = Scanner("")
    _ = s.next()
    assert not s.has_next(), (
        "Next should have moved pointed ahead and no longer have next token"
    )


def test_peek_doesnt_move_ahead():
    s = Scanner("")
    _ = s.peek()
    assert s.has_next(), "Peek shouldn't have altered postition"


def test_scan_basic_identifiers():
    s = Scanner("abc aBC a_BC a0b a0_1Bb")
    assert s.next() == Token(TokenType.IDENTIFIER, "abc")
    assert s.next() == Token(TokenType.IDENTIFIER, "aBC")
    assert s.next() == Token(TokenType.IDENTIFIER, "a_BC")
    assert s.next() == Token(TokenType.IDENTIFIER, "a0b")
    assert s.next() == Token(TokenType.IDENTIFIER, "a0_1Bb")


def test_raises_on_invalid_identifiers():
    s = Scanner("ab@")
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == 'Klein Lexical Error at Line 0 Position 2: Invalid character "@" in identifier. Only alphanumeric characters and underscores allowed.'
    )

    s = Scanner("ab" + chr(11))
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == 'Klein Lexical Error at Line 0 Position 2: Invalid character "utf8:11" in identifier. Only alphanumeric characters and underscores allowed.'
    )


def test_max_identifier_boundary():
    ident_256 = "abcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdef"
    s = Scanner(
        ident_256,
    )
    assert s.next() == Token(TokenType.IDENTIFIER, ident_256)

    ident_257 = ident_256 + "g"

    s = Scanner(
        ident_257,
    )
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == "Klein Lexical Error at Line 0 Position 257: Identifiers cannot be longer than 256 characters"
    )


def test_scan_basic_ints():
    s = Scanner("0 123 1234567 1000")
    assert s.next() == Token(TokenType.INTEGER, "0")
    assert s.next() == Token(TokenType.INTEGER, "123")
    assert s.next() == Token(TokenType.INTEGER, "1234567")
    assert s.next() == Token(TokenType.INTEGER, "1000")


def test_raises_on_invalid_ints():
    s = Scanner("01")
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == "Klein Lexical Error at Line 0 Position 1: Integer cannot start with leading 0"
    ), "Should show custom message about no leading 0 for integers"

    s = Scanner("0k")
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == 'Klein Lexical Error at Line 0 Position 1: Invalid character "k" in integer'
    ), "Should show message about unknown character in integer"

    s = Scanner("100k")
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == 'Klein Lexical Error at Line 0 Position 3: Invalid character "k" in integer'
    ), "Should show message about unknown character in integer"


def test_detects_special_identifiers():
    s = Scanner("integer boolean true false if then else not and or function print")
    assert s.next() == Token(TokenType.KEYWORD, "integer")
    assert s.next() == Token(TokenType.KEYWORD, "boolean")
    assert s.next() == Token(TokenType.BOOLEAN, "true"), (
        "Should use correct token class for true boolean"
    )
    assert s.next() == Token(TokenType.BOOLEAN, "false"), (
        "Should use correct token class for false boolean"
    )
    assert s.next() == Token(TokenType.KEYWORD, "if")
    assert s.next() == Token(TokenType.KEYWORD, "then")
    assert s.next() == Token(TokenType.KEYWORD, "else")
    assert s.next() == Token(TokenType.KEYWORD, "not")
    assert s.next() == Token(TokenType.KEYWORD, "and")
    assert s.next() == Token(TokenType.KEYWORD, "or")
    assert s.next() == Token(TokenType.KEYWORD, "function")
    assert s.next() == Token(TokenType.PRIMITIVE_IDENTIFIER, "print")


def test_detects_operators():
    s = Scanner("+ - / * < =")
    assert s.next() == Token(TokenType.PLUS)
    assert s.next() == Token(TokenType.MINUS)
    assert s.next() == Token(TokenType.DIVIDE)
    assert s.next() == Token(TokenType.TIMES)
    assert s.next() == Token(TokenType.LESS_THAN)
    assert s.next() == Token(TokenType.EQUAL)


def test_detects_punctuation():
    s = Scanner("( ) , :")
    assert s.next() == Token(TokenType.LEFT_PAREN)
    assert s.next() == Token(TokenType.RIGHT_PAREN)
    assert s.next() == Token(TokenType.COMMA)
    assert s.next() == Token(TokenType.COLON)


def test_whitespace_ignored():
    s = Scanner(" a\tb\nc\rd")
    assert s.next() == Token(TokenType.IDENTIFIER, "a"), "Ignores a space"
    assert s.next() == Token(TokenType.IDENTIFIER, "b"), "Ignores a tab"
    assert s.next() == Token(TokenType.IDENTIFIER, "c"), "Ignores a newline"
    assert s.next() == Token(TokenType.IDENTIFIER, "d"), "Ignores a carriage return"


def test_comments_ignored():
    s = Scanner(
        "(* this is a long\t\n\rmultiine comment that 012 contains in&!@^#valid identifiers * ) (* and more *)",
    )
    assert s.next() == Token(TokenType.END_OF_FILE)


def test_trailing_comment_raises():
    s = Scanner("(* test")
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == "Klein Lexical Error at Line 0 Position 7: All comments must be terminated before program ends"
    )


def test_delimiters_function():
    s = Scanner("abc(abc)abc:abc,abc+abc/")
    delimiter_types = [
        TokenType.LEFT_PAREN,
        TokenType.RIGHT_PAREN,
        TokenType.COLON,
        TokenType.COMMA,
        TokenType.PLUS,
        TokenType.DIVIDE,
    ]
    for delimiter_type in delimiter_types:
        assert s.next() == Token(TokenType.IDENTIFIER, "abc")
        assert s.next() == Token(delimiter_type)
