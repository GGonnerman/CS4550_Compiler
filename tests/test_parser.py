from pathlib import Path

import pytest

from compiler.klein_errors import ParseError
from compiler.parser import Parser
from compiler.scanner import Scanner


def test_parse_empty_file():
    s = Scanner("")
    p = Parser(s)
    assert p.parse() is None


def test_minimal():
    s = Scanner("""
    function test(): integer
        1
    """)
    p = Parser(s)
    assert p.parse() is None, "Simple program should parse"


def test_parameters():
    s = Scanner("""
    function test(a : integer): integer
        1
    """)
    p = Parser(s)
    assert p.parse() is None, "Program should allow single integer parameters"

    s = Scanner("""
    function test(a : boolean): integer
        1
    """)
    p = Parser(s)
    assert p.parse() is None, "Program should allow single boolean parameters"

    s = Scanner("""
    function test(a : integer, b : boolean, c: integer): integer
        1
    """)
    p = Parser(s)
    assert p.parse() is None, "Program should allow multiple parameters"


def test_invalid_parameter():
    s = Scanner("""
    function test(12): integer
        1
    """)
    p = Parser(s)
    with pytest.raises(ParseError) as excinfo:
        p.parse()
    # assert excinfo, "Program should raise if integer literal given as parameter"
    s = Scanner("""
    function test((): integer
        1
    """)
    p = Parser(s)
    with pytest.raises(ParseError) as excinfo:
        p.parse()
    s = Scanner("""
    function test(a): integer
        1
    """)
    p = Parser(s)
    with pytest.raises(ParseError) as excinfo:
        p.parse()
    # assert excinfo, "Program should raise if parameter missing colon and type"
    s = Scanner("""
    function test(a:): integer
        1
    """)
    p = Parser(s)
    with pytest.raises(ParseError) as excinfo:
        p.parse()
    # assert excinfo, "Program should raise if parameter missing type"
    s = Scanner("""
    function test(a integer): integer
        1
    """)
    p = Parser(s)
    with pytest.raises(ParseError) as excinfo:
        p.parse()
    # assert excinfo, "Program should raise if parameter missing colon"


def test_return_type():
    s = Scanner("""
    function test(): integer
        1
    """)
    p = Parser(s)
    assert p.parse() is None, "Program should allow integer return type"

    s = Scanner("""
    function test(): boolean
        1
    """)
    p = Parser(s)
    assert p.parse() is None, "Program should allow boolean return type"


def test_invalid_return_type():
    s = Scanner("""
    function test(): function
        1
    """)
    p = Parser(s)
    with pytest.raises(ParseError) as excinfo:
        p.parse()
    # assert excinfo, "Program should raise on function return type"

    s = Scanner("""
    function test(): 123
        1
    """)
    p = Parser(s)
    with pytest.raises(ParseError) as excinfo:
        p.parse()
    # assert excinfo, "Program should raise on integer literal return type"

    s = Scanner("""
    function test(): random_identifier
        1
    """)
    p = Parser(s)
    with pytest.raises(ParseError) as excinfo:
        p.parse()
    # assert excinfo, "Program should raise on random identifier as return type"


def test_all_programs():
    program_path = Path(__file__).parent / "programs"
    for file in program_path.glob("*.kln"):
        # This program is currently invalid
        if str(file).endswith("egyptian-factions.kln"):
            continue
        path = program_path / file
        s = Scanner(path.open().read())
        p = Parser(s)
        assert p.parse() is None
