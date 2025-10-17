from pathlib import Path

import pytest

from compiler.ast import (
    AndExpression,
    Argument,
    ArgumentList,
    ASTNode,
    Body,
    BooleanLiteral,
    BooleanType,
    Definition,
    DefinitionList,
    DivideExpression,
    EqualsExpression,
    FunctionCallExpression,
    Identifier,
    IdWithType,
    IfExpression,
    IntegerLiteral,
    IntegerType,
    LessThanExpression,
    MinusExpression,
    NotExpression,
    OrExpression,
    ParameterList,
    PlusExpression,
    Program,
    TimesExpression,
    UnaryMinusExpression,
)
from compiler.klein_errors import ParseError
from compiler.parser import Parser
from compiler.scanner import Scanner


def blueprint(*definitions: Definition) -> Program:
    return Program(DefinitionList(list(definitions)))


def success_case(program: str, expected_result: ASTNode, error_message: str):
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
        _ = p.parse()
    # TODO: In theory this should actually test it against a specific error message
    # but for now just erroring is acceptable.
    # assert str(excinfo.value) == expected_message, error_message


def test_parse_empty_file():
    success_case(
        "",
        Program(DefinitionList([])),
        "Empty program (no defintions) should parse",
    )


def test_parse_definitions():
    success_case(
        """
    function test(): integer
        1
    """,
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList([]),
                IntegerType(),
                Body([], IntegerLiteral("1")),
            ),
        ),
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
        blueprint(
            Definition(
                Identifier("a"),
                ParameterList([]),
                IntegerType(),
                Body([], IntegerLiteral("1")),
            ),
            Definition(
                Identifier("b"),
                ParameterList([]),
                IntegerType(),
                Body([], IntegerLiteral("2")),
            ),
            Definition(
                Identifier("c"),
                ParameterList([]),
                IntegerType(),
                Body([], IntegerLiteral("3")),
            ),
            Definition(
                Identifier("d"),
                ParameterList([]),
                IntegerType(),
                Body([], IntegerLiteral("4")),
            ),
        ),
        "Program with many definitions should parse",
    )


def test_expression_order():
    success_case(
        """
    function test(): integer
        1 + 2 + 3 or 4
    """,
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList([]),
                IntegerType(),
                Body(
                    [],
                    OrExpression(
                        PlusExpression(
                            PlusExpression(
                                IntegerLiteral("1"),
                                IntegerLiteral("2"),
                            ),
                            IntegerLiteral("3"),
                        ),
                        IntegerLiteral("4"),
                    ),
                ),
            ),
        ),
        "Operators with same priority should execute left-to-right",
    )

    success_case(
        """
    function test(): integer
        1 * 2 + 3
    """,
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList([]),
                IntegerType(),
                Body(
                    [],
                    PlusExpression(
                        TimesExpression(
                            IntegerLiteral("1"),
                            IntegerLiteral("2"),
                        ),
                        IntegerLiteral("3"),
                    ),
                ),
            ),
        ),
        "Times should bind closer than plus",
    )

    success_case(
        """
    function test(): integer
        1 + 2 * 3
    """,
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList([]),
                IntegerType(),
                Body(
                    [],
                    PlusExpression(
                        IntegerLiteral("1"),
                        TimesExpression(
                            IntegerLiteral("2"),
                            IntegerLiteral("3"),
                        ),
                    ),
                ),
            ),
        ),
        "Times should bind closer than plus",
    )

    success_case(
        """
    function test(): integer
        (1 + 2) * 3
    """,
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList([]),
                IntegerType(),
                Body(
                    [],
                    TimesExpression(
                        PlusExpression(
                            IntegerLiteral("1"),
                            IntegerLiteral("2"),
                        ),
                        IntegerLiteral("3"),
                    ),
                ),
            ),
        ),
        "Parenthesis should force close binding",
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


def test_invalid_body():
    error_case(
        """
    function a() integer
        print(123)
    """,
        None,
        "No return in body",
    )


def test_return_type():
    success_case(
        """
    function test(): integer
        1
    """,
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList([]),
                IntegerType(),
                Body([], IntegerLiteral("1")),
            ),
        ),
        "Program should allow integer return type",
    )

    success_case(
        """
    function test(): boolean
        true
    """,
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList([]),
                BooleanType(),
                Body([], BooleanLiteral("true")),
            ),
        ),
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
    function test():
        1
    """,
        None,
        "Program should raise on no return type",
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
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList(
                    [
                        IdWithType(Identifier("a"), IntegerType()),
                    ],
                ),
                IntegerType(),
                Body([], IntegerLiteral("1")),
            ),
        ),
        "Program should allow single integer parameters",
    )

    success_case(
        """
    function test(a : boolean): integer
        1
    """,
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList(
                    [
                        IdWithType(Identifier("a"), BooleanType()),
                    ],
                ),
                IntegerType(),
                Body([], IntegerLiteral("1")),
            ),
        ),
        "Program should allow single boolean parameters",
    )

    success_case(
        """
    function test(a : integer, b : boolean, c: integer): integer
        1
    """,
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList(
                    [
                        IdWithType(Identifier("a"), IntegerType()),
                        IdWithType(Identifier("b"), BooleanType()),
                        IdWithType(Identifier("c"), IntegerType()),
                    ],
                ),
                IntegerType(),
                Body([], IntegerLiteral("1")),
            ),
        ),
        "Program should allow multiple parameters",
    )


def test_invalid_parameter():
    error_case(
        """
    function test(12 : integer): integer
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
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList([IdWithType(Identifier("a"), IntegerType())]),
                IntegerType(),
                Body(
                    [
                        FunctionCallExpression(
                            Identifier("print"),
                            ArgumentList([Argument(IntegerLiteral("12"))]),
                        ),
                    ],
                    IntegerLiteral("1"),
                ),
            ),
        ),
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
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList([IdWithType(Identifier("a"), IntegerType())]),
                IntegerType(),
                Body(
                    [
                        FunctionCallExpression(
                            Identifier("print"),
                            ArgumentList([Argument(IntegerLiteral("1"))]),
                        ),
                        FunctionCallExpression(
                            Identifier("print"),
                            ArgumentList([Argument(IntegerLiteral("2"))]),
                        ),
                        FunctionCallExpression(
                            Identifier("print"),
                            ArgumentList([Argument(IntegerLiteral("3"))]),
                        ),
                    ],
                    IntegerLiteral("1"),
                ),
            ),
        ),
        "Program should allow multiple print statements",
    )

    success_case(
        """
    function test(a : integer): integer
        print(not 12 or 3 + 4 * 5)
        1
    """,
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList([IdWithType(Identifier("a"), IntegerType())]),
                IntegerType(),
                Body(
                    [
                        FunctionCallExpression(
                            Identifier("print"),
                            ArgumentList(
                                [
                                    Argument(
                                        PlusExpression(
                                            OrExpression(
                                                NotExpression(IntegerLiteral("12")),
                                                IntegerLiteral("3"),
                                            ),
                                            TimesExpression(
                                                IntegerLiteral("4"),
                                                IntegerLiteral("5"),
                                            ),
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ],
                    IntegerLiteral("1"),
                ),
            ),
        ),
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

    error_case(
        program="""
        function test(a : integer): integer
            1
            print()
        """,
        expected_message=None,
        error_message="Program should raise on print not being the first part of body",
    )


def test_argument_list():
    success_case(
        """
        function add(): integer
            1

        function main(): integer
            add()
        """,
        blueprint(
            Definition(
                Identifier("add"),
                ParameterList([]),
                IntegerType(),
                Body([], IntegerLiteral("1")),
            ),
            Definition(
                Identifier("main"),
                ParameterList([]),
                IntegerType(),
                Body([], FunctionCallExpression(Identifier("add"), ArgumentList([]))),
            ),
        ),
        "Empty argument list should work",
    )

    success_case(
        """
        function add(): integer
            1
        function main(): integer
            add(1)
        """,
        blueprint(
            Definition(
                Identifier("add"),
                ParameterList([]),
                IntegerType(),
                Body([], IntegerLiteral("1")),
            ),
            Definition(
                Identifier("main"),
                ParameterList([]),
                IntegerType(),
                Body(
                    [],
                    FunctionCallExpression(
                        Identifier("add"),
                        ArgumentList([Argument(IntegerLiteral("1"))]),
                    ),
                ),
            ),
        ),
        "Single argument should work",
    )

    success_case(
        """
        function add(): integer
            1
        function main(): integer
            add(1, 2, 3, 4)
        """,
        blueprint(
            Definition(
                Identifier("add"),
                ParameterList([]),
                IntegerType(),
                Body([], IntegerLiteral("1")),
            ),
            Definition(
                Identifier("main"),
                ParameterList([]),
                IntegerType(),
                Body(
                    [],
                    FunctionCallExpression(
                        Identifier("add"),
                        ArgumentList(
                            [
                                Argument(IntegerLiteral("1")),
                                Argument(IntegerLiteral("2")),
                                Argument(IntegerLiteral("3")),
                                Argument(IntegerLiteral("4")),
                            ],
                        ),
                    ),
                ),
            ),
        ),
        "Many arguments should work",
    )

    success_case(
        """
        function add(): integer
            1
        function main(): integer
            add(1 * 2 + 3 and 4, 5 * 6 or 7 and add(1))
        """,
        blueprint(
            Definition(
                Identifier("add"),
                ParameterList([]),
                IntegerType(),
                Body([], IntegerLiteral("1")),
            ),
            Definition(
                Identifier("main"),
                ParameterList([]),
                IntegerType(),
                Body(
                    [],
                    FunctionCallExpression(
                        Identifier("add"),
                        ArgumentList(
                            [
                                Argument(
                                    PlusExpression(
                                        TimesExpression(
                                            IntegerLiteral("1"),
                                            IntegerLiteral("2"),
                                        ),
                                        AndExpression(
                                            IntegerLiteral("3"),
                                            IntegerLiteral("4"),
                                        ),
                                    ),
                                ),
                                Argument(
                                    OrExpression(
                                        TimesExpression(
                                            IntegerLiteral("5"),
                                            IntegerLiteral("6"),
                                        ),
                                        AndExpression(
                                            IntegerLiteral("7"),
                                            FunctionCallExpression(
                                                Identifier("add"),
                                                ArgumentList(
                                                    [Argument(IntegerLiteral("1"))],
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ),
                ),
            ),
        ),
        "Complex arguments should work",
    )


def test_invalid_argument_list():
    error_case(
        """
        function add(): integer
            1
        function main(): integer
            add(1, )
        """,
        None,
        "Trailing comma in argument list",
    )

    error_case(
        """
        function add(): integer
            1
        function main(): integer
            add(a : integer)
        """,
        None,
        "ID with type in argument list",
    )


def test_term():
    success_case(
        """
        function add(): integer
            1 * true * 3 * false / 5 / true and 7 and false and 9
        """,
        blueprint(
            Definition(
                Identifier("add"),
                ParameterList([]),
                IntegerType(),
                Body(
                    [],
                    AndExpression(
                        AndExpression(
                            AndExpression(
                                DivideExpression(
                                    DivideExpression(
                                        TimesExpression(
                                            TimesExpression(
                                                TimesExpression(
                                                    IntegerLiteral("1"),
                                                    BooleanLiteral("true"),
                                                ),
                                                IntegerLiteral("3"),
                                            ),
                                            BooleanLiteral("false"),
                                        ),
                                        IntegerLiteral("5"),
                                    ),
                                    BooleanLiteral("true"),
                                ),
                                IntegerLiteral("7"),
                            ),
                            BooleanLiteral("false"),
                        ),
                        IntegerLiteral("9"),
                    ),
                ),
            ),
        ),
        "Any valid terms should work",
    )

    success_case(
        """
        function add(): integer
            1 * my_fun(12) / 2 * (1 + 2)
        """,
        blueprint(
            Definition(
                Identifier("add"),
                ParameterList([]),
                IntegerType(),
                Body(
                    [],
                    TimesExpression(
                        DivideExpression(
                            TimesExpression(
                                IntegerLiteral("1"),
                                FunctionCallExpression(
                                    Identifier("my_fun"),
                                    ArgumentList(
                                        [
                                            Argument(
                                                IntegerLiteral("12"),
                                            ),
                                        ],
                                    ),
                                ),
                            ),
                            IntegerLiteral("2"),
                        ),
                        PlusExpression(
                            IntegerLiteral("1"),
                            IntegerLiteral("2"),
                        ),
                    ),
                ),
            ),
        ),
        "Complex terms with factors inside should work",
    )


def test_invalid_term():
    error_case(
        """
        function add(): integer
            1 * / 2
        """,
        None,
        "Term rest (times) followed by non-term (division) should fail",
    )

    error_case(
        """
        function add(): integer
            1 / function
        """,
        None,
        "Term rest (division) by non-term (function keyword) should fail",
    )

    error_case(
        """
        function add(): integer
            1 and or 2
        """,
        None,
        "Term rest (and) by non-term ('or') should fail",
    )


def test_factor():
    success_case(
        """
        function add(): integer
            1 and
            true and
            not 2 and
            my_id and
            my_fun(3, 4) and
            if true then 5 else 6 and
            ( 7 * 8 )
        """,
        blueprint(
            Definition(
                Identifier("add"),
                ParameterList([]),
                IntegerType(),
                Body(
                    [],
                    AndExpression(
                        AndExpression(
                            AndExpression(
                                AndExpression(
                                    AndExpression(
                                        IntegerLiteral("1"),
                                        BooleanLiteral("true"),
                                    ),
                                    NotExpression(IntegerLiteral("2")),
                                ),
                                Identifier("my_id"),
                            ),
                            FunctionCallExpression(
                                Identifier("my_fun"),
                                ArgumentList(
                                    [
                                        Argument(IntegerLiteral("3")),
                                        Argument(IntegerLiteral("4")),
                                    ],
                                ),
                            ),
                        ),
                        IfExpression(
                            BooleanLiteral("true"),
                            IntegerLiteral("5"),
                            AndExpression(
                                IntegerLiteral("6"),
                                TimesExpression(
                                    IntegerLiteral("7"),
                                    IntegerLiteral("8"),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
        "Any valid factor should work",
    )


def test_invalid_factor():
    error_case(
        """
        function add(): integer
            not integer
        """,
        None,
        "Not followed by non-factor (type) should fail",
    )

    error_case(
        """
        function add(): integer
            - :
        """,
        None,
        "Minus followed by non-factor (colon) should fail",
    )

    error_case(
        """
        function add(): integer
            my_id my_id
        """,
        None,
        "Identifieir followed by non-factor rest (another identifier) should fail",
    )

    error_case(
        """
        function add(): integer
            if true
                1
            else
                2
        """,
        None,
        "If statement missing then should fail",
    )

    error_case(
        """
        function add(): integer
            if true
            then 1
        """,
        None,
        "If statement missing else should fail",
    )

    error_case(
        """
        function add(): integer
            ()
        """,
        None,
        "Factor missing expression inside of parens should fail",
    )


def test_simple_expression():
    success_case(
        """
    function test(): integer
        1 or 2 or 3 + 4 + 5 - 6 - 7
    """,
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList([]),
                IntegerType(),
                Body(
                    [],
                    MinusExpression(
                        MinusExpression(
                            PlusExpression(
                                PlusExpression(
                                    OrExpression(
                                        OrExpression(
                                            IntegerLiteral("1"),
                                            IntegerLiteral("2"),
                                        ),
                                        IntegerLiteral("3"),
                                    ),
                                    IntegerLiteral("4"),
                                ),
                                IntegerLiteral("5"),
                            ),
                            IntegerLiteral("6"),
                        ),
                        IntegerLiteral("7"),
                    ),
                ),
            ),
        ),
        "Many simple expressions in a row should work",
    )

    success_case(
        """
    function test(): integer
        1 or (2 or (3 + 4) - 5) - (6 + 7)
    """,
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList([]),
                IntegerType(),
                Body(
                    [],
                    MinusExpression(
                        OrExpression(
                            IntegerLiteral("1"),
                            MinusExpression(
                                OrExpression(
                                    IntegerLiteral("2"),
                                    PlusExpression(
                                        IntegerLiteral("3"),
                                        IntegerLiteral("4"),
                                    ),
                                ),
                                IntegerLiteral("5"),
                            ),
                        ),
                        PlusExpression(IntegerLiteral("6"), IntegerLiteral("7")),
                    ),
                ),
            ),
        ),
        "Simple expression should allow nested complex expressions",
    )

    success_case(
        """
    function test(): integer
        1 - - 2
    """,
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList([]),
                IntegerType(),
                Body(
                    [],
                    MinusExpression(
                        IntegerLiteral("1"),
                        UnaryMinusExpression(
                            IntegerLiteral("2"),
                        ),
                    ),
                ),
            ),
        ),
        "Adding a negative value should be allowed",
    )
    success_case(
        """
    function test(): boolean
        1 < 2 = (3 < 4)
    """,
        blueprint(
            Definition(
                Identifier("test"),
                ParameterList([]),
                BooleanType(),
                Body(
                    [],
                    EqualsExpression(
                        LessThanExpression(
                            IntegerLiteral("1"),
                            IntegerLiteral("2"),
                        ),
                        LessThanExpression(
                            IntegerLiteral("3"),
                            IntegerLiteral("4"),
                        ),
                    ),
                ),
            ),
        ),
        "Nested comparisons should parse",
    )


def test_invalid_simple_expression():
    error_case(
        """
    function test(): integer
        1 or or 2
    """,
        None,
        "Repeated 'or' statement should fail",
    )

    error_case(
        """
    function test(): integer
        1 + boolean
    """,
        None,
        "Plus statement followed by type should fail",
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
        _ = p.parse()
