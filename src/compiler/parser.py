from compiler.ast import ASTNode, SemanticAction, SemanticStack, action_to_astnode
from compiler.klein_errors import ParseError
from compiler.parse_table import NonTerminal, generate_parse_table
from compiler.scanner import Scanner
from compiler.tokens import Token, TokenType


class Parser:
    def __init__(self, scanner: Scanner, parse_table_filename: str = "parse-table.csv"):
        self._scanner: Scanner = scanner
        self._parse_table: dict[
            tuple[NonTerminal, TokenType],
            list[NonTerminal | TokenType | SemanticAction],
        ] = generate_parse_table(parse_table_filename)

    def _generate_expected_options(
        self,
        next_stack_item: NonTerminal | TokenType,
    ) -> str:
        options: list[str] = []
        for token_type in TokenType:
            if (next_stack_item, token_type) in self._parse_table:
                options.append(str(token_type))  # noqa: PERF401
        expected_message = ""
        if len(options) <= 1:
            expected_message = f"Expected {options[0]}."
        else:
            expected_message = (
                f"Expected one of the following options: {', '.join(options)}."
            )
        return expected_message

    def parse(self) -> ASTNode:
        stack: list[NonTerminal | TokenType | SemanticAction] = [
            TokenType.END_OF_FILE,
            NonTerminal.PROGRAM,
        ]
        semantic_stack: SemanticStack = SemanticStack()
        most_recent_token: Token | None = None

        while len(stack) > 0:
            next_stack_item: NonTerminal | TokenType | SemanticAction = stack.pop()
            if isinstance(next_stack_item, TokenType):
                # next stack item is a token, so pop the next token and check if
                # it equals the next scanner value if so, continue
                # otherwise, raise a parse error
                next_token = self._scanner.next()
                most_recent_token = next_token
                if next_stack_item != next_token.token_type:
                    raise ParseError(
                        f"Expected {next_stack_item} and received {next_token.token_type}",
                        position=next_token.position,
                        original_line=self._scanner.get_line(
                            next_token.position.get_line_number() - 1,
                        ),
                    )
            elif isinstance(next_stack_item, NonTerminal):
                # Know we know a is a NonTerminal
                next_token = self._scanner.peek()
                most_recent_token = next_token
                key = (next_stack_item, next_token.token_type)
                if key in self._parse_table:
                    # If we have a rule, add theh tokens/nonterminals onto the stack
                    # in reverse order
                    rule = self._parse_table[(next_stack_item, next_token.token_type)]
                    stack.extend(reversed(rule))
                else:
                    # Otherwise, find all could-be tokens to let the user know what
                    # might have been expected and report those.
                    expected_message: str = self._generate_expected_options(
                        next_stack_item,
                    )
                    raise ParseError(
                        f"Invalid transition from {key[0]} to {key[1]}.\n{expected_message}",
                        position=next_token.position,
                        original_line=self._scanner.get_line(
                            next_token.position.get_line_number() - 1,
                        ),
                    )
            elif isinstance(next_stack_item, SemanticAction):  # pyright: ignore[reportUnnecessaryIsInstance]
                action = action_to_astnode[next_stack_item]
                astnode = action(semantic_stack, most_recent_token)
                semantic_stack.push(astnode)
            else:
                raise ParseError(  # pyright: ignore[reportUnreachable]
                    f"Unexpected value on stack: Received {next_stack_item} of type {next_stack_item.__class__.__name__}",
                )

        if len(semantic_stack) != 1:
            raise ParseError(
                f"Expected 1 value in semantic stack when done parsing. Instead encountered {len(semantic_stack)} items: {semantic_stack}",
            )

        return semantic_stack.pop()
