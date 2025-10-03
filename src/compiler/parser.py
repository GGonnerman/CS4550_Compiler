from compiler.klein_errors import ParseError
from compiler.parse_table import NonTerminal, generate_parse_table
from compiler.scanner import Scanner
from compiler.tokens import TokenType


class Parser:
    def __init__(self, scanner: Scanner, parse_table_filename: str = "parse-table.csv"):
        self._scanner: Scanner = scanner
        self._parse_table: dict[
            tuple[NonTerminal, TokenType],
            list[NonTerminal | TokenType],
        ] = generate_parse_table(parse_table_filename)

    def parse(self) -> None:
        stack: list[NonTerminal | TokenType] = [
            TokenType.END_OF_FILE,
            NonTerminal.PROGRAM,
        ]

        while len(stack) > 0:
            a = stack[-1]
            if isinstance(a, TokenType):
                # a is a token, so pop the next token and check if it equals a
                # if so, continue
                # otherwise, raise a parse error
                next_token = self._scanner.next()
                _ = stack.pop()
                if a == next_token.token_type:
                    continue
                raise ParseError(
                    f"Expected {a} and received {next_token.token_type} on {next_token.position}",
                )
            # Know we know a is a NonTerminal
            next_token = self._scanner.peek()
            key = (a, next_token.token_type)
            if key in self._parse_table:
                # If we have a rule, add theh tokens/nonterminals onto the stack
                # in reverse order
                rule = self._parse_table[(a, next_token.token_type)]
                _ = stack.pop()
                stack.extend(reversed(rule))
            else:
                # Otherwise, find all could-be tokens to let the user know what
                # might have been expected and report those.
                options: list[str] = []
                for token_type in TokenType:
                    if (a, token_type) in self._parse_table:
                        options.append(str(token_type))  # noqa: PERF401
                expected_message = ""
                if len(options) <= 1:
                    expected_message = f"Expected {options[0]}."
                else:
                    expected_message = (
                        f"Expected one of the following options: {', '.join(options)}."
                    )

                raise ParseError(
                    f"Invalid sequence {key[0]} followed by {key[1]} on {next_token.position}. {expected_message}",
                )
