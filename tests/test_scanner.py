import pytest

from compiler.klein_errors import KleinError, LexicalError
from compiler.position import Position
from compiler.scanner import Scanner
from compiler.tokens import Token, TokenType


def test_scan_end_of_file():
    s = Scanner("")
    assert s.has_next(), "Empty file should have next input (EOF char)"
    assert s.next() == TokenType.END_OF_FILE, (
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


def test_unknown_character():
    s = Scanner("_hi")
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == 'Klein Lexical Error at Line 1 Position 0: Illegal character "_" when looking for\nnext token.'
    )
    s = Scanner("@hi")
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == 'Klein Lexical Error at Line 1 Position 0: Illegal character "@" when looking for\nnext token.'
    )


def test_scan_basic_identifiers():
    s = Scanner("abc aBC a_BC a0b a0_1Bb adsf89__09123d____")
    assert s.next() == Token(Position(1, 0, 0), TokenType.IDENTIFIER, "abc")
    assert s.next() == Token(Position(1, 4, 4), TokenType.IDENTIFIER, "aBC")
    assert s.next() == Token(Position(1, 8, 8), TokenType.IDENTIFIER, "a_BC")
    assert s.next() == Token(Position(1, 13, 13), TokenType.IDENTIFIER, "a0b")
    assert s.next() == Token(Position(1, 17, 17), TokenType.IDENTIFIER, "a0_1Bb")
    assert s.next() == Token(
        Position(1, 24, 24),
        TokenType.IDENTIFIER,
        "adsf89__09123d____",
    )


def test_raises_on_invalid_identifiers():
    s = Scanner("ab@")
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == 'Klein Lexical Error at Line 1 Position 2: Invalid character "@" in identifier.\nOnly alphanumeric characters and underscores allowed.'
    )

    s = Scanner("ab" + chr(11))
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == 'Klein Lexical Error at Line 1 Position 2: Invalid character "utf8:11" in\nidentifier. Only alphanumeric characters and underscores allowed.'
    )


def test_max_identifier_boundary():
    ident_256 = "abcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdef"
    s = Scanner(
        ident_256,
    )
    assert s.next() == Token(Position(1, 0, 0), TokenType.IDENTIFIER, ident_256)

    ident_257 = ident_256 + "g"

    s = Scanner(
        ident_257,
    )
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == "Klein Lexical Error at Line 1 Position 257: Identifiers cannot be longer than\n256 characters"
    )


def test_scan_basic_ints():
    s = Scanner("0 123 1234567 1000")
    assert s.next() == Token(Position(1, 0, 0), TokenType.INTEGER, "0")
    assert s.next() == Token(Position(1, 2, 2), TokenType.INTEGER, "123")
    assert s.next() == Token(Position(1, 6, 6), TokenType.INTEGER, "1234567")
    assert s.next() == Token(Position(1, 14, 14), TokenType.INTEGER, "1000")


def test_raises_on_invalid_ints():
    s = Scanner("01")
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == "Klein Lexical Error at Line 1 Position 1: Integer cannot start with leading 0"
    ), "Should show custom message about no leading 0 for integers"

    s = Scanner("0k")
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == 'Klein Lexical Error at Line 1 Position 1: Invalid character "k" in integer'
    ), "Should show message about invalid character in integer"

    s = Scanner("100k")
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == 'Klein Lexical Error at Line 1 Position 3: Invalid character "k" in integer'
    ), "Should show message about invalid character in integer"


def test_integer_bounds():
    s = Scanner("0")
    assert s.next() == Token(Position(1, 0, 0), TokenType.INTEGER, "0")
    int_limit = (2**31) - 1
    s = Scanner(str(int_limit))
    assert s.next() == Token(Position(1, 0, 0), TokenType.INTEGER, str(int_limit))
    overflow = int_limit + 1
    s = Scanner(str(overflow))
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == "Klein Lexical Error at Line 1 Position 10: Integer literal must be bounded\nbetween 0 (incl) and 2147483647 (incl)."
    )
    s = Scanner(str(overflow) + ")")
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == "Klein Lexical Error at Line 1 Position 10: Integer literal must be bounded\nbetween 0 (incl) and 2147483647 (incl)."
    )


def test_detects_keywords():
    s = Scanner("integer boolean true false if then else not and or function print")
    assert s.next() == Token(Position(1, 0, 0), TokenType.KEYWORD_INTEGER)
    assert s.next() == Token(Position(1, 8, 8), TokenType.KEYWORD_BOOLEAN)
    assert s.next() == Token(Position(1, 16, 16), TokenType.BOOLEAN, "true"), (
        "Should use correct token class for true boolean"
    )
    assert s.next() == Token(Position(1, 21, 21), TokenType.BOOLEAN, "false"), (
        "Should use correct token class for false boolean"
    )
    assert s.next() == Token(Position(1, 27, 27), TokenType.KEYWORD_IF)
    assert s.next() == Token(Position(1, 30, 30), TokenType.KEYWORD_THEN)
    assert s.next() == Token(Position(1, 35, 35), TokenType.KEYWORD_ELSE)
    assert s.next() == Token(Position(1, 40, 40), TokenType.KEYWORD_NOT)
    assert s.next() == Token(Position(1, 44, 44), TokenType.KEYWORD_AND)
    assert s.next() == Token(Position(1, 48, 48), TokenType.KEYWORD_OR)
    assert s.next() == Token(Position(1, 51, 51), TokenType.KEYWORD_FUNCTION)
    assert s.next() == Token(Position(1, 60, 60), TokenType.KEYWORD_PRINT)


def test_detects_operators():
    s = Scanner("+ - / * < =")
    assert s.next() == TokenType.PLUS
    assert s.next() == TokenType.MINUS
    assert s.next() == TokenType.DIVIDE
    assert s.next() == TokenType.TIMES
    assert s.next() == TokenType.LESS_THAN
    assert s.next() == TokenType.EQUAL


def test_detects_punctuation():
    s = Scanner("( ) , : (")
    assert s.next() == TokenType.LEFT_PAREN
    assert s.next() == TokenType.RIGHT_PAREN
    assert s.next() == TokenType.COMMA
    assert s.next() == TokenType.COLON
    assert s.next() == TokenType.LEFT_PAREN


def test_whitespace_ignored():
    s = Scanner(" a\tb\nc\rd")
    assert s.next() == Token(Position(1, 1, 1), TokenType.IDENTIFIER, "a"), (
        "Ignores a space"
    )
    assert s.next() == Token(Position(1, 3, 3), TokenType.IDENTIFIER, "b"), (
        "Ignores a tab"
    )
    assert s.next() == Token(Position(2, 0, 5), TokenType.IDENTIFIER, "c"), (
        "Ignores a newline"
    )
    assert s.next() == Token(Position(2, 2, 7), TokenType.IDENTIFIER, "d"), (
        "Ignores a carriage return"
    )


def test_comments_ignored():
    s = Scanner(
        "(* this is a long\t\n\rmultiine comment that 012 contains in&!@^#valid identifiers * ) (* and more *)",
    )
    assert s.next() == Token(Position(2, 79, 98), TokenType.END_OF_FILE)
    s = Scanner(
        "(**)",
    )
    assert s.next() == Token(Position(1, 4, 4), TokenType.END_OF_FILE)
    s = Scanner(
        "(* *)",
    )
    assert s.next() == Token(Position(1, 5, 5), TokenType.END_OF_FILE)


def test_trailing_comment_raises():
    s = Scanner("(* test")
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == "Klein Lexical Error at Line 1 Position 7: All comments must be terminated before\nprogram ends"
    )
    s = Scanner("(* test*")
    with pytest.raises(LexicalError) as excinfo:
        _ = s.next()
    assert (
        str(excinfo.value)
        == "Klein Lexical Error at Line 1 Position 8: All comments must be terminated before\nprogram ends"
    )


def test_position_tracks():
    s = Scanner("hey\nhi\n1223  function \r once")
    for _ in s:
        pass

    assert s.position.get_position() == 21
    assert s.position.get_absolute_position() == 28
    assert s.position.get_line_number() == 3


def test_position_tracks_in_comment():
    s = Scanner("(* \n *\n ) \r\n * \n ) *)")
    _ = s.next()
    assert s.position.get_position() == 5, "Correct counting of spaces after newline"
    assert s.position.get_absolute_position() == 21, (
        "Absolute position updated across comment"
    )
    assert s.position.get_line_number() == 5
    s = Scanner("(* *)Hi")
    _ = s.next()
    assert s.position.get_position() == 7, "Correct counting of spaces after newline"
    assert s.position.get_absolute_position() == 7, (
        "Absolute position updated across comment"
    )
    assert s.position.get_line_number() == 1


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
        assert s.next() == TokenType.IDENTIFIER
        assert s.next() == delimiter_type


def test_scanner_iter():
    s = Scanner("abc\nabc\rabc")
    tokens = [
        Token(Position(1, 0, 0), TokenType.IDENTIFIER, "abc"),
        Token(Position(2, 0, 4), TokenType.IDENTIFIER, "abc"),
        Token(Position(2, 4, 8), TokenType.IDENTIFIER, "abc"),
        Token(Position(2, 7, 11), TokenType.END_OF_FILE),
    ]
    for token in s:
        assert token == tokens[0]
        _ = tokens.pop(0)
