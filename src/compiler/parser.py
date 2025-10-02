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
                next_token = self._scanner.next()
                _ = stack.pop()
                if a == next_token.token_type:
                    print(next_token)
                    continue
                raise ParseError(
                    f"Was at {a} and got {next_token.token_type}. Erroring",
                )
            # Know we know a is a NonTerminal
            next_token = self._scanner.peek()
            key = (a, next_token.token_type)
            if key in self._parse_table:
                rule = self._parse_table[(a, next_token.token_type)]
                _ = stack.pop()
                print(f"Saw {key} adding {[n.name for n in (reversed(rule))]}")
                stack.extend(reversed(rule))
            else:
                raise ParseError(f"Was at couldnt find rule for {key}. Erroring")
