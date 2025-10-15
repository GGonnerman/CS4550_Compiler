from abc import ABC
from collections.abc import Callable
from enum import StrEnum, auto
from typing import TypeVar

from typing_extensions import override

from compiler.tokens import Token, TokenType

T = TypeVar("T")


class SemanticStack:
    def __init__(self) -> None:
        self._stack: list[ASTNode] = []

    def pop_if(self, desired_type: type[T]) -> T | None:
        if self.is_empty():
            return None
        top_node = self.peek()
        if isinstance(top_node, desired_type):
            _ = self.pop()
            return top_node
        return None

    def push(self, node: "ASTNode") -> None:
        self._stack.append(node)

    def pop(self) -> "ASTNode":
        return self._stack.pop()

    def peek(self) -> "ASTNode":
        return self._stack[-1]

    def is_empty(self) -> int:
        return len(self._stack) == 0

    def __len__(self) -> int:
        return len(self._stack)

    @override
    def __str__(self) -> str:
        return ",".join([str(x) for x in self._stack])


class SemanticAction(StrEnum):
    MAKE_PROGRAM = auto()
    MAKE_DEFINITION_LIST = auto()
    MAKE_DEFINITION = auto()
    MAKE_IDENTIFIER = auto()
    MAKE_PARAMETER_LIST = auto()
    MAKE_ID_WITH_TYPE = auto()
    MAKE_INTEGER_TYPE = auto()
    MAKE_BOOLEAN_TYPE = auto()
    MAKE_BODY = auto()
    MAKE_FUNCTION_CALL_EXPRESSION = auto()
    MAKE_EQUALS_EXPRESSION = auto()
    MAKE_LESS_THAN_EXPRESSION = auto()
    MAKE_OR_EXPRESSION = auto()
    MAKE_PLUS_EXPRESSION = auto()
    MAKE_MINUS_EXPRESSION = auto()
    MAKE_TIMES_EXPRESSION = auto()
    MAKE_DIVIDE_EXPRESSION = auto()
    MAKE_AND_EXPRESSION = auto()
    MAKE_NOT_EXPRESSION = auto()
    MAKE_UNARY_MINUS_EXPRESSION = auto()
    MAKE_IF_EXPRESSION = auto()
    MAKE_ARGUMENT_LIST = auto()
    MAKE_ARGUMENT = auto()
    MAKE_INTEGER_LITERAL = auto()
    MAKE_BOOLEAN_LITERAL = auto()


class ASTNode(ABC):  # noqa: B024
    def validate(self, node: "ASTNode", desired_type: type[T]) -> T:
        if not isinstance(node, desired_type):
            raise TypeError(
                f"Expected {node} to be type {desired_type.__name__} instead found {node.__class__.__name__}",  # noqa: E501
            )
        return node

    def ensure_token(self, token: Token | None) -> Token:
        if token is None:
            raise ValueError(
                f"No most recent token found when generating {self.__class__.__name__}",
            )
        return token

    def __str__(self) -> str:
        return self.__class__.__name__

    def get_token_value(self, token: Token) -> str:
        value = token.value()
        if value is None:
            raise ValueError(
                f"Most recent token missing value found when generating {self.__class__.__name__}: {token}",
            )
        return value


class Program(ASTNode):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self.definition_list: DefinitionList = self.validate(
            semantic_stack.pop(),
            DefinitionList,
        )


class DefinitionList(ASTNode):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self.definitions: list[Definition] = []
        while not semantic_stack.is_empty():
            next_node = semantic_stack.pop_if(Definition)
            if next_node:
                self.definitions.insert(0, next_node)
            else:
                break


class Definition(ASTNode):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self.body: Body = self.validate(semantic_stack.pop(), Body)
        self.return_type: Type = self.validate(semantic_stack.pop(), Type)
        self.parameters: ParameterList = self.validate(
            semantic_stack.pop(),
            ParameterList,
        )
        self.name: Identifier = self.validate(semantic_stack.pop(), Identifier)


class ParameterList(ASTNode):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self.definitions: list[IdWithType] = []
        while not semantic_stack.is_empty():
            next_node = semantic_stack.pop_if(IdWithType)
            if next_node:
                self.definitions.insert(0, next_node)
            else:
                break


class Body(ASTNode):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self.body: Expression = self.validate(semantic_stack.pop(), Expression)
        self.print_expressions: list[FunctionCallExpression] = []
        while not semantic_stack.is_empty():
            next_node = semantic_stack.pop_if(FunctionCallExpression)
            if next_node:
                self.print_expressions.insert(0, next_node)
            else:
                break


class IdWithType(ASTNode):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self.type: Type = self.validate(semantic_stack.pop(), Type)
        self.name: Identifier = self.validate(semantic_stack.pop(), Identifier)


class Type(ASTNode, ABC):
    pass


class IntegerType(Type):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        pass

    def __str__(self):
        return "Integer"


class BooleanType(Type):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        pass

    def __str__(self):
        return "Boolean"


class Expression(ASTNode, ABC):
    pass


class UnaryExpression(Expression, ABC):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self.value: Expression = self.validate(semantic_stack.pop(), Expression)


class BinaryExpression(Expression, ABC):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self.right_side: Expression = self.validate(semantic_stack.pop(), Expression)
        self.left_side: Expression = self.validate(semantic_stack.pop(), Expression)


class EqualsExpression(BinaryExpression):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        super().__init__(semantic_stack, most_recent_token)


class LessThanExpression(BinaryExpression):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        super().__init__(semantic_stack, most_recent_token)


class OrExpression(BinaryExpression):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        super().__init__(semantic_stack, most_recent_token)


class PlusExpression(BinaryExpression):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        super().__init__(semantic_stack, most_recent_token)


class MinusExpression(BinaryExpression):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        super().__init__(semantic_stack, most_recent_token)


class TimesExpression(BinaryExpression):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        super().__init__(semantic_stack, most_recent_token)


class DivideExpression(BinaryExpression):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        super().__init__(semantic_stack, most_recent_token)


class AndExpression(BinaryExpression):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        super().__init__(semantic_stack, most_recent_token)


class NotExpression(UnaryExpression):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        super().__init__(semantic_stack, most_recent_token)


class UnaryMinusExpression(UnaryExpression):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        super().__init__(semantic_stack, most_recent_token)


class IfExpression(Expression):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self.condition: Expression = self.validate(semantic_stack.pop(), Expression)
        self.consequent: Expression = self.validate(semantic_stack.pop(), Expression)
        self.alternative: Expression = self.validate(semantic_stack.pop(), Expression)


class FunctionCallExpression(Expression):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self.argument_list: ArgumentList = self.validate(
            semantic_stack.pop(),
            ArgumentList,
        )
        self.function_name: Identifier = self.validate(semantic_stack.pop(), Identifier)


class ArgumentList(ASTNode):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self.arguments: list[Argument] = []
        while not semantic_stack.is_empty():
            next_node = semantic_stack.pop_if(Argument)
            if next_node:
                self.arguments.insert(0, next_node)
            else:
                break


class Argument(ASTNode):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self.value: Expression = self.validate(semantic_stack.pop(), Expression)


class Literal(Expression, ABC):
    pass


class IntegerLiteral(Literal):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self._token: Token = self.ensure_token(most_recent_token)
        self.value: str = self.get_token_value(self._token)


class BooleanLiteral(Literal):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self._token: Token = self.ensure_token(most_recent_token)
        self.value: str = self.get_token_value(self._token)


class Identifier(Expression):
    def __init__(self, semantic_stack: SemanticStack, most_recent_token: Token | None):
        self._token: Token = self.ensure_token(most_recent_token)
        self.value: str
        if self._token == TokenType.KEYWORD_PRINT:
            self.value = "print"
        else:
            self.value = self.get_token_value(self._token)

    def __str__(self):
        return f"{self.value}"


action_to_astnode: dict[
    SemanticAction,
    Callable[[SemanticStack, Token | None], ASTNode],
] = {
    SemanticAction.MAKE_PROGRAM: Program,
    SemanticAction.MAKE_DEFINITION_LIST: DefinitionList,
    SemanticAction.MAKE_DEFINITION: Definition,
    SemanticAction.MAKE_IDENTIFIER: Identifier,
    SemanticAction.MAKE_PARAMETER_LIST: ParameterList,
    SemanticAction.MAKE_ID_WITH_TYPE: IdWithType,
    SemanticAction.MAKE_INTEGER_TYPE: IntegerType,
    SemanticAction.MAKE_BOOLEAN_TYPE: BooleanType,
    SemanticAction.MAKE_BODY: Body,
    SemanticAction.MAKE_FUNCTION_CALL_EXPRESSION: FunctionCallExpression,
    SemanticAction.MAKE_EQUALS_EXPRESSION: EqualsExpression,
    SemanticAction.MAKE_LESS_THAN_EXPRESSION: LessThanExpression,
    SemanticAction.MAKE_OR_EXPRESSION: OrExpression,
    SemanticAction.MAKE_PLUS_EXPRESSION: PlusExpression,
    SemanticAction.MAKE_MINUS_EXPRESSION: MinusExpression,
    SemanticAction.MAKE_TIMES_EXPRESSION: TimesExpression,
    SemanticAction.MAKE_DIVIDE_EXPRESSION: DivideExpression,
    SemanticAction.MAKE_AND_EXPRESSION: AndExpression,
    SemanticAction.MAKE_NOT_EXPRESSION: NotExpression,
    SemanticAction.MAKE_UNARY_MINUS_EXPRESSION: UnaryMinusExpression,
    SemanticAction.MAKE_IF_EXPRESSION: IfExpression,
    SemanticAction.MAKE_ARGUMENT_LIST: ArgumentList,
    SemanticAction.MAKE_ARGUMENT: Argument,
    SemanticAction.MAKE_INTEGER_LITERAL: IntegerLiteral,
    SemanticAction.MAKE_BOOLEAN_LITERAL: BooleanLiteral,
}


def display_astnode(node: ASTNode, indent: int = 0, spacer: str = "  "):
    main_indent: str = indent * spacer
    sub_indent: str = (indent + 1) * spacer
    if isinstance(node, Program):
        print(f"{main_indent}{node}")
        display_astnode(node.definition_list, indent + 1, spacer)
    elif isinstance(node, DefinitionList):
        for definition in node.definitions:
            display_astnode(definition, indent, spacer)
    elif isinstance(node, Definition):
        print(f"{main_indent}{node}")
        print(f"{sub_indent}name {node.name}")
        print(f"{sub_indent}parameters")
        display_astnode(node.parameters, indent + 2, spacer)
        print(f"{sub_indent}returns {node.return_type}")
        print(f"{sub_indent}body")
        display_astnode(node.body, indent + 2, spacer)
    elif isinstance(node, ParameterList):
        for parameter in node.definitions:
            display_astnode(parameter, indent, spacer)
    elif isinstance(node, IdWithType):
        print(f"{main_indent}{node.type} {node.name}")
    elif isinstance(node, Body):
        for print_stm in node.print_expressions:
            display_astnode(print_stm, indent, spacer)
        display_astnode(node.body, indent, spacer)
    elif isinstance(node, FunctionCallExpression):
        print(f"{main_indent}function call")
        print(f"{sub_indent}name {node.function_name}")
        display_astnode(node.argument_list, indent + 1, spacer)
    elif isinstance(node, ArgumentList):
        if len(node.arguments) == 0:
            return
        print(f"{main_indent}arguments")
        for argument in node.arguments:
            display_astnode(argument, indent + 1, spacer)
    elif isinstance(node, Argument):
        display_astnode(node.value, indent, spacer)
    elif isinstance(node, BinaryExpression):
        print(f"{main_indent}{node}")
        if isinstance(node.left_side, (Identifier, Literal)):
            print(f"{sub_indent}left_side {node.left_side}")
        else:
            print(f"{sub_indent}left_side")
            display_astnode(node.left_side, indent + 2, spacer)
        if isinstance(node.right_side, (Identifier, Literal)):
            print(f"{sub_indent}right_side {node.right_side}")
        else:
            print(f"{sub_indent}right_side")
            display_astnode(node.right_side, indent + 2, spacer)
    elif isinstance(node, UnaryExpression):
        print(f"{main_indent}{node}")
        if isinstance(node.value, (Identifier, Literal)):
            print(f"{sub_indent}value {node.value}")
        else:
            print(f"{sub_indent}value")
            display_astnode(node.value, indent + 2, spacer)
    elif isinstance(node, (IntegerLiteral, BooleanLiteral)):
        print(f"{main_indent}{node} {node.value}")
    elif isinstance(node, Identifier):
        print(f"{main_indent}{node.value}")
    else:
        raise NotImplementedError(f"Node of type {node} has not yet been implemented")


def astnode_to_dot(node: ASTNode):
    print("digraph ast {")
    _astnode_to_dot(node)
    print("}")


def link(source: ASTNode, destination: ASTNode, label: str | None = None):
    if label:
        print(f'{hash(source)} -> {hash(destination)} [label = "{label}"]')
    else:
        print(f"{hash(source)} -> {hash(destination)}")
    _astnode_to_dot(destination)


def _astnode_to_dot(node: ASTNode):
    key = hash(node)
    if isinstance(node, Program):
        print(f'{key} [label = "{node}"]')
        link(node, node.definition_list)
    elif isinstance(node, DefinitionList):
        print(f'{key} [label = "{node}"]')
        for definition in node.definitions:
            link(node, definition)
    elif isinstance(node, Definition):
        print(
            f'{key} [label = "{node}\nname: {node.name}\nreturns {node.return_type}"]',
        )
        # link(node, node.name, "name")

        link(node, node.parameters, "parameters")
        link(node, node.body, "body")
    elif isinstance(node, ParameterList):
        print(f'{key} [label = "{node}"]')
        for parameter in node.definitions:
            link(node, parameter)
    elif isinstance(node, IdWithType):
        print(f'{key} [label = "name {node.name}\ntype {node.type}"]')
    elif isinstance(node, Body):
        print(f'{key} [label = "{node}"]')
        for print_expression in node.print_expressions:
            link(node, print_expression)
        link(node, node.body)
    elif isinstance(node, BinaryExpression):
        print(f'{key} [label = "{node}"]')
        link(node, node.left_side, "left_side")
        link(node, node.right_side, "right_side")
    elif isinstance(node, UnaryExpression):
        print(f'{key} [label = "{node}"]')
        link(node, node.value)
    elif isinstance(node, FunctionCallExpression):
        print(f'{key} [label = "{node}\n{node.function_name}"]')
        link(node, node.argument_list)
    elif isinstance(node, ArgumentList):
        print(f'{key} [label = "{node}"]')
        for argument in node.arguments:
            link(node, argument)
    elif isinstance(node, Argument):
        print(f'{key} [label = "{node}"]')
        link(node, node.value)
    elif isinstance(node, IfExpression):
        print(f'{key} [label = "{node}"]')
        link(node, node.condition, "condition")
        link(node, node.consequent, "consequent")
        link(node, node.alternative, "alternative")
    elif isinstance(node, (Identifier, IntegerLiteral, BooleanLiteral)):
        # TODO: Check if this seems right
        print(f'{key} [label = "{node}"]')
    else:
        return
