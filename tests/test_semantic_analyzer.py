from io import StringIO
from unittest.mock import patch

import pytest

from compiler.klein_errors import SemanticError
from compiler.parser import Parser
from compiler.scanner import Scanner
from compiler.semantic_analyzer import SemanticAnalyzer


@patch("sys.stdout", new_callable=StringIO)
def assume_fails(program: str, expected_output: list[str], mock_stdout: StringIO):
    semantic_analyzer = SemanticAnalyzer(
        Parser(
            Scanner(program),
        ).parse(),
    )
    with pytest.raises(SemanticError) as excinfo:
        semantic_analyzer.annotate()
    semantic_analyzer.display_issues()
    assert mock_stdout.getvalue() == "\n".join(expected_output) + "\n"


class TestSemanticAnalyzer:
    @patch("sys.stdout", new_callable=StringIO)
    def test_warns_on_unused(self, mock_stdout: StringIO):
        semantic_analyzer = SemanticAnalyzer(
            Parser(
                Scanner(
                    """
            function unused_fun(unused_arg: integer): integer
                1
            function main(): integer
                1
        """,
                ),
            ).parse(),
        )
        semantic_analyzer.annotate()
        semantic_analyzer.display_issues()
        assert (
            mock_stdout.getvalue()
            == "\n".join(
                [
                    "Klein Semantic Warning: Function unused_fun: Unused parameter unused_arg",
                    "Klein Semantic Warning: Unused function unused_fun",
                ],
            )
            + "\n"
        )

    def test_wrong_return_integer(self):
        assume_fails(
            """
                function main(): integer
                    true
            """,
            [
                "Klein Semantic Error: Expected function main to return Integer instead found Boolean",
            ],
        )

    def test_wrong_return_boolean(self):
        assume_fails(
            """
                function main(): boolean
                    1
            """,
            [
                "Klein Semantic Error: Expected function main to return Boolean instead found Integer",
            ],
        )

    def test_duplicated_fun_name(self):
        assume_fails(
            """
                function duplicated_fun_name(): integer
                    1

                function duplicated_fun_name(): integer
                    1

                function main(): integer
                    duplicated_fun_name() + duplicated_fun_name()
            """,
            ["Klein Semantic Error: Duplicated function name duplicated_fun_name"],
        )

    def test_duplicated_arg_name(self):
        assume_fails(
            """
                function main(duplicated_arg: integer, duplicated_arg: integer): integer
                    duplicated_arg
            """,
            [
                "Klein Semantic Error: Function main: Duplicated parameter name duplicated_arg",
            ],
        )

    def test_wrong_expression_children(self):
        assume_fails(
            """
    function main(): boolean
        print(true + true)
        print(1 + true)
        print(true - false)
        print(1 - false)
        print(false * true)
        print(1 * true)
        print(false / false)
        print(1 / false)
        print(true < true)
        print(1 < true)
        print(not 1)
        print(2 and 3)
        print(true and 3)
        print(4 or 5)
        print(false or 5)
        true
            """,
            [
                "Klein Semantic Error: Function main: Expected left side of PlusExpression to be Integer instead found Boolean",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Expected right side of PlusExpression to be Integer instead found Boolean",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Expected left side of MinusExpression to be Integer instead found Boolean",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Expected right side of MinusExpression to be Integer instead found Boolean",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Expected left side of TimesExpression to be Integer instead found Boolean",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Expected right side of TimesExpression to be Integer instead found Boolean",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Expected left side of DivideExpression to be Integer instead found Boolean",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Expected right side of DivideExpression to be Integer instead found Boolean",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Expected left side of LessThanExpression to be Integer instead found Boolean",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Expected right side of LessThanExpression to be Integer instead found Boolean",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Expected value of NotExpression to be Boolean instead found Integer",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Expected left side of AndExpression to be Boolean instead found Integer",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Expected right side of AndExpression to be Boolean instead found Integer",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Expected left side of OrExpression to be Boolean instead found Integer",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Expected right side of OrExpression to be Boolean instead found Integer",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
            ],
        )

    def test_if_called_with_int_as_conditional(self):
        assume_fails(
            """
        function main(): integer
            if 1 then 2 else 3
        """,
            [
                "Klein Semantic Error: Function main: Expected condition of IfExpression to be Boolean instead found Integer",
                "Klein Semantic Error: Expected function main to return Integer instead found Error",
            ],
        )

    def test_if_indeterminate_return_raises(self):
        assume_fails(
            """
        function main(): integer
            if true then 2 else false
        """,
            [
                "Klein Semantic Error: Expected function main to return Integer instead found {Integer OR Boolean}",
            ],
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_indeterminate_in_print_doesnt_raise(self, mock_stdout: StringIO):
        SemanticAnalyzer(
            Parser(
                Scanner(
                    """
                            function main(): integer
                                print(if true then 1 else false)
                                print(if true then false else 1)
                                1
                            """,
                ),
            ).parse(),
        ).annotate()
        assert mock_stdout.getvalue() == ""

    def test_if_with_multiple_issues(self):
        assume_fails(
            """
        function main(): integer
            if 1 then 2 else false
        """,
            [
                "Klein Semantic Error: Function main: Expected condition of IfExpression to be Boolean instead found Integer",
                "Klein Semantic Error: Expected function main to return Integer instead found Error",
            ],
        )

    def test_return_wrong_type(self):
        assume_fails(
            """
            function main(): integer
                true
            """,
            [
                "Klein Semantic Error: Expected function main to return Integer instead found Boolean",
            ],
        )

        assume_fails(
            """
            function main(): boolean
                1
            """,
            [
                "Klein Semantic Error: Expected function main to return Boolean instead found Integer",
            ],
        )

    def test_return_function(self):
        assume_fails(
            """
            function returns_int(): integer
                1
            function main(): boolean
                returns_int()
            """,
            [
                "Klein Semantic Error: Expected function main to return Boolean instead found Integer",
            ],
        )

    def test_call_nonexistant_fun(self):
        assume_fails(
            """
            function main(): integer
                nonexistant_fun()
            """,
            [
                "Klein Semantic Error: Function main: Attempted to call non-existant function nonexistant_fun",
                "Klein Semantic Error: Expected function main to return Integer instead found Error",
            ],
        )

    def test_call_param_as_fun(self):
        assume_fails(
            """
            function main(int_param: integer): integer
                int_param()
            """,
            [
                "Klein Semantic Error: Function main: Attempted to call parameter int_param as a function",
                "Klein Semantic Warning: Function main: Unused parameter int_param",
                "Klein Semantic Error: Expected function main to return Integer instead found Error",
            ],
        )

    def test_uses_nonexistant_param(self):
        assume_fails(
            """
            function main(): integer
                1 + nonexistant_param
            """,
            [
                "Klein Semantic Error: Function main: Missing identifier nonexistant_param referenced",
                "Klein Semantic Error: Function main: Expected right side of PlusExpression to be Integer instead found Error",
                "Klein Semantic Error: Expected function main to return Integer instead found Error",
            ],
        )

    def test_uses_function_as_identifier(self):
        assume_fails(
            """
            function my_fun(): integer
                1
            function main(): integer
                1 + my_fun
            """,
            [
                "Klein Semantic Error: Function main: Attempted to use function my_fun as identifier",
                "Klein Semantic Error: Function main: Expected right side of PlusExpression to be Integer instead found Error",
                "Klein Semantic Error: Expected function main to return Integer instead found Error",
                "Klein Semantic Warning: Unused function my_fun",
            ],
        )

    def test_bubble_up_errors(self):
        assume_fails(
            """
        function main(): integer
            false + 2 + 3 + 4 + 5
        """,
            [
                "Klein Semantic Error: Function main: Expected left side of PlusExpression to be Integer instead found Boolean",
                "Klein Semantic Error: Function main: Expected left side of PlusExpression to be Integer instead found Error",
                "Klein Semantic Error: Function main: Expected left side of PlusExpression to be Integer instead found Error",
                "Klein Semantic Error: Function main: Expected left side of PlusExpression to be Integer instead found Error",
                "Klein Semantic Error: Expected function main to return Integer instead found Error",
            ],
        )

    def test_wrong_fun_params(self):
        assume_fails(
            """
            function main(): integer
                print(bool_typing(1))
                print(int_typing(true))
                print(sequential_typing(1, 2, false))
                print(one_param(1, 2))
                print(three_params(1, 2))
                1
            function bool_typing(wrong_type: boolean): boolean
                wrong_type
            function int_typing(wrong_type:integer): integer
                wrong_type
            function sequential_typing(a: integer, b: boolean, c: boolean): integer
                if b and c then a else 1
            function one_param(param: integer): integer
                param
            function three_params(a: integer, b: integer, c: integer): integer
                a + b + c
        """,
            [
                "Klein Semantic Error: Function main: Mismatched argument types passed to bool_typing. Expected (Boolean) and received (Integer)",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Mismatched argument types passed to int_typing. Expected (Integer) and received (Boolean)",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Mismatched argument types passed to sequential_typing. Expected (Integer, Boolean, Boolean) and received (Integer, Integer, Boolean)",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Too many arguments passed to one_param. Expected 1 and receieved 2",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
                "Klein Semantic Error: Function main: Too few arguments passed to three_params. Expected 3 and receieved 2",
                "Klein Semantic Error: Function main: Mismatched argument types passed to print. Expected ({Integer OR Boolean}) and received (Error)",
            ],
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_safe_recursive_fun(self, mock_stdout: StringIO):
        SemanticAnalyzer(
            Parser(
                Scanner(
                    """
                            function recursive_fun(a: integer): integer
                                if a < 1
                                then a
                                else a + recursive_fun(a - 1)
                            function main(a: integer): integer
                                recursive_fun(a)
                            """,
                ),
            ).parse(),
        ).annotate()
        assert mock_stdout.getvalue() == ""

    def test_bad_recursive_fun(self):
        assume_fails(
            """
        function recursive_fun(a: integer): integer
            if a < 1
            then a
            else a + recursive_fun(if true then a else false)
        function main(a: integer): integer
            recursive_fun(a)
        """,
            [
                "Klein Semantic Error: Function recursive_fun: Mismatched argument types passed to recursive_fun. Expected (Integer) and received ({Integer OR Boolean})",
                "Klein Semantic Error: Function recursive_fun: Expected right side of PlusExpression to be Integer instead found Error",
                "Klein Semantic Error: Expected function recursive_fun to return Integer instead found {Integer OR Error}",
            ],
        )

    def test_missing_main_fun(self):
        assume_fails(
            """
        function missing_main(a: integer): integer
            if a = 0
            then 1
            else missing_main(a - 1)
        """,
            [
                "Klein Semantic Error: Missing a main function",
            ],
        )
