from pathlib import Path

import pytest

from compiler.klein_errors import ParseError
from compiler.parser import Parser
from compiler.scanner import Scanner


def success_case(program: str, expected_result: str | None, error_message: str):
    s = Scanner(program)
    p = Parser(s)
    assert p.parse() == expected_result, error_message


def error_case(
    program: str,
    expected_message: str | None,
    error_message: str,
):
    s = Scanner(program)
    p = Parser(s)
    with pytest.raises(ParseError) as excinfo:
        p.parse()
    # assert str(excinfo) == expected_message, error_message


def test_parse_empty_file():
    success_case("", None, "Empty program (no defintions) should parse")


def test_parse_definitions():
    success_case(
        """
    function test(): integer
        1
    """,
        None,
        "Program with single definition should parse",
    )

    success_case(
        """
    function a(): integer
        1
    function b(): integer
        2
    function c(): integer
        3
    function d(): integer
        4
    """,
        None,
        "Program with many definitions should parse",
    )


def test_raises_invalid_definition():
    error_case(
        """
    function (): integer
        1
    """,
        None,
        "No identifier for definition name",
    )

    error_case(
        """
    function a() integer
        1
    """,
        None,
        "No colon inside of definition",
    )

    error_case(
        """
    function a() integer
    """,
        None,
        "No body in definition",
    )


def test_return_type():
    success_case(
        """
    function test(): integer
        1
    """,
        None,
        "Program should allow integer return type",
    )

    success_case(
        """
    function test(): boolean
        1
    """,
        None,
        "Program should allow boolean return type",
    )


def test_invalid_return_type():
    error_case(
        """
    function test(): function
        1
    """,
        None,
        "Program should raise on function return type",
    )

    error_case(
        """
    function test(): 123
        1
    """,
        None,
        "Program should raise on integer literal return type",
    )

    error_case(
        """
    function test(): random_identifier
        1
    """,
        None,
        "Program should raise on random identifier as return type",
    )


def test_parameters():
    success_case(
        """
    function test(a : integer): integer
        1
    """,
        None,
        "Program should allow single integer parameters",
    )

    success_case(
        """
    function test(a : boolean): integer
        1
    """,
        None,
        "Program should allow single boolean parameters",
    )

    success_case(
        """
    function test(a : integer, b : boolean, c: integer): integer
        1
    """,
        None,
        "Program should allow multiple parameters",
    )


def test_invalid_parameter():
    error_case(
        """
    function test(12): integer
        1
    """,
        None,
        "Program should raise if integer literal given as parameter",
    )

    error_case(
        """
    function test((): integer
        1
    """,
        None,
        "Program should raise if parameter is start paren",
    )
    error_case(
        """
    function test(a): integer
        1
    """,
        None,
        "Program should raise if parameter missing colon and type",
    )
    error_case(
        """
    function test(a:): integer
        1
    """,
        None,
        "Program should raise if parameter missing type",
    )
    error_case(
        """
    function test(a integer): integer
        1
    """,
        None,
        "Program should raise if parameter missing colon",
    )
    error_case(
        """
    function test(a : integer, ): integer
        1
    """,
        None,
        "Program should raise if trailing comma",
    )


def test_print_expression():
    success_case(
        """
    function test(a : integer): integer
        print(12)
        1
    """,
        None,
        "Program should allow print statements",
    )

    success_case(
        """
    function test(a : integer): integer
        print(1)
        print(2)
        print(3)
        1
    """,
        None,
        "Program should allow multiple print statements",
    )

    success_case(
        """
    function test(a : integer): integer
        print(not 12 or 3 + 4 * 5)
        1
    """,
        None,
        "Program should allow complex print statements",
    )


def test_raises_invalid_print():
    error_case(
        """
    function test(a : integer): integer
        print(or 12)
        1
    """,
        None,
        "Program should riase on invalid body of print",
    )

    error_case(
        """
        function test(a : integer): integer
            print()
            1
        """,
        None,
        "Program should raise on empty print",
    )


def test_all_programs():
    program_path = Path(__file__).parent / "programs"
    for file in program_path.glob("*.kln"):
        # This program is currently invalid
        if str(file).endswith("egyptian-fractions.kln"):
            continue
        path = program_path / file
        s = Scanner(path.open().read())
        p = Parser(s)
        assert p.parse() is None
