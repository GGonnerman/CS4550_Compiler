from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import StrEnum, auto
from typing import Self, TypeVar

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


class ASTNode(ABC):
    @override
    def __str__(self) -> str:
        return self.__class__.__name__

    @classmethod
    def get_token_value(cls, token: Token | None) -> str:
        if token is None:
            raise ValueError(
                f"No most recent token found when generating {cls.__name__}",
            )
        value = token.value()
        if value is None:
            raise ValueError(
                f"Most recent token missing value found when generating {cls.__name__}: {token}",
            )
        return value

    @classmethod
    def validate(cls, node: "ASTNode", desired_type: type[T]) -> T:
        if not isinstance(node, desired_type):
            raise TypeError(
                f"Expected {node} to be type {desired_type.__name__} instead found {node.__class__.__name__}",
            )
        return node

    @classmethod
    @abstractmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> Self: ...


class Program(ASTNode):
    def __init__(self, definition_list: "DefinitionList"):
        self.definition_list: DefinitionList = definition_list

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: "SemanticStack",
        most_recent_token: Token | None,
    ) -> "Program":
        definition_list: DefinitionList = cls.validate(
            semantic_stack.pop(),
            DefinitionList,
        )
        return Program(definition_list)


class DefinitionList(ASTNode):
    def __init__(self, definitions: list["Definition"]):
        self.definitions: list[Definition] = definitions

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> "DefinitionList":
        definitions: list[Definition] = []
        while not semantic_stack.is_empty():
            next_node = semantic_stack.pop_if(Definition)
            if next_node:
                definitions.insert(0, next_node)
            else:
                break
        return DefinitionList(definitions)


class Definition(ASTNode):
    def __init__(
        self,
        name: "Identifier",
        parameters: "ParameterList",
        return_type: "Type",
        body: "Body",
    ):
        self.name: Identifier = name
        self.parameters: ParameterList = parameters
        self.return_type: Type = return_type
        self.body: Body = body

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> "Definition":
        body: Body = cls.validate(semantic_stack.pop(), Body)
        return_type: Type = cls.validate(semantic_stack.pop(), Type)
        parameters: ParameterList = cls.validate(
            semantic_stack.pop(),
            ParameterList,
        )
        name: Identifier = cls.validate(semantic_stack.pop(), Identifier)
        return Definition(name, parameters, return_type, body)


class ParameterList(ASTNode):
    def __init__(self, definitions: list["IdWithType"]):
        self.definitions: list[IdWithType] = definitions

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> "ParameterList":
        definitions: list[IdWithType] = []
        while not semantic_stack.is_empty():
            next_node = semantic_stack.pop_if(IdWithType)
            if next_node:
                definitions.insert(0, next_node)
            else:
                break
        return ParameterList(definitions)


class Body(ASTNode):
    def __init__(
        self,
        print_expressions: list["FunctionCallExpression"],
        body: "Expression",
    ):
        self.print_expressions: list[FunctionCallExpression] = print_expressions
        self.body: Expression = body

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> "Body":
        body: Expression = cls.validate(semantic_stack.pop(), Expression)
        print_expressions: list[FunctionCallExpression] = []
        while not semantic_stack.is_empty():
            next_node = semantic_stack.pop_if(FunctionCallExpression)
            if next_node:
                print_expressions.insert(0, next_node)
            else:
                break
        return Body(print_expressions, body)


class IdWithType(ASTNode):
    def __init__(self, name: "Identifier", type_node: "Type"):
        self.name: Identifier = name
        self.type: Type = type_node

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> "IdWithType":
        type_node: Type = cls.validate(semantic_stack.pop(), Type)
        name: Identifier = cls.validate(semantic_stack.pop(), Identifier)
        return IdWithType(name, type_node)


class Type(ASTNode, ABC):
    pass


class IntegerType(Type):
    def __init__(self):
        pass

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> "IntegerType":
        return IntegerType()

    @override
    def __str__(self):
        return "Integer"


class BooleanType(Type):
    def __init__(self):
        pass

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> "BooleanType":
        return BooleanType()

    @override
    def __str__(self):
        return "Boolean"


class Expression(ASTNode, ABC):
    pass


class UnaryExpression(Expression, ABC):
    def __init__(self, value: Expression):
        self.value: Expression = value

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> Self:
        value: Expression = cls.validate(semantic_stack.pop(), Expression)
        return cls(value)


class BinaryExpression(Expression, ABC):
    def __init__(self, left_side: Expression, right_side: Expression):
        self.left_side: Expression = left_side
        self.right_side: Expression = right_side

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> Self:
        right_side: Expression = cls.validate(semantic_stack.pop(), Expression)
        left_side: Expression = cls.validate(semantic_stack.pop(), Expression)
        return cls(left_side, right_side)


class EqualsExpression(BinaryExpression):
    def __init__(self, left_side: Expression, right_side: Expression):
        super().__init__(left_side, right_side)


class LessThanExpression(BinaryExpression):
    def __init__(self, left_side: Expression, right_side: Expression):
        super().__init__(left_side, right_side)


class OrExpression(BinaryExpression):
    def __init__(self, left_side: Expression, right_side: Expression):
        super().__init__(left_side, right_side)


class PlusExpression(BinaryExpression):
    def __init__(self, left_side: Expression, right_side: Expression):
        super().__init__(left_side, right_side)


class MinusExpression(BinaryExpression):
    def __init__(self, left_side: Expression, right_side: Expression):
        super().__init__(left_side, right_side)


class TimesExpression(BinaryExpression):
    def __init__(self, left_side: Expression, right_side: Expression):
        super().__init__(left_side, right_side)


class DivideExpression(BinaryExpression):
    def __init__(self, left_side: Expression, right_side: Expression):
        super().__init__(left_side, right_side)


class AndExpression(BinaryExpression):
    def __init__(self, left_side: Expression, right_side: Expression):
        super().__init__(left_side, right_side)


class NotExpression(UnaryExpression):
    def __init__(self, value: Expression):
        super().__init__(value)


class UnaryMinusExpression(UnaryExpression):
    def __init__(self, value: Expression):
        super().__init__(value)


class IfExpression(Expression):
    def __init__(
        self,
        condition: Expression,
        consequent: Expression,
        alternative: Expression,
    ):
        self.condition: Expression = condition
        self.consequent: Expression = consequent
        self.alternative: Expression = alternative

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> "IfExpression":
        condition: Expression = cls.validate(semantic_stack.pop(), Expression)
        consequent: Expression = cls.validate(semantic_stack.pop(), Expression)
        alternative: Expression = cls.validate(semantic_stack.pop(), Expression)
        return IfExpression(condition, consequent, alternative)


class FunctionCallExpression(Expression):
    def __init__(self, function_name: "Identifier", argument_list: "ArgumentList"):
        self.function_name: Identifier = function_name
        self.argument_list: ArgumentList = argument_list

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> "FunctionCallExpression":
        argument_list: ArgumentList = cls.validate(
            semantic_stack.pop(),
            ArgumentList,
        )
        function_name: Identifier = cls.validate(semantic_stack.pop(), Identifier)
        return FunctionCallExpression(function_name, argument_list)


class ArgumentList(ASTNode):
    def __init__(self, arguments: list["Argument"]):
        self.arguments: list[Argument] = arguments

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> "ArgumentList":
        arguments: list[Argument] = []
        while not semantic_stack.is_empty():
            next_node = semantic_stack.pop_if(Argument)
            if next_node:
                arguments.insert(0, next_node)
            else:
                break
        return ArgumentList(arguments)


class Argument(ASTNode):
    def __init__(self, value: Expression):
        self.value: Expression = value

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> Self:
        value: Expression = cls.validate(semantic_stack.pop(), Expression)
        return cls(value)


class Literal(Expression, ABC):
    def __init__(self, value: str):
        self.value: str = value

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> Self:
        value = cls.get_token_value(most_recent_token)
        return cls(value)


class IntegerLiteral(Literal):
    @override
    def __str__(self):
        return f"IntegerLiteral {self.value}"


class BooleanLiteral(Literal):
    @override
    def __str__(self):
        return f"BooleanLiteral {self.value}"


class Identifier(Expression):
    def __init__(self, value: str):
        self.value: str = value

    @override
    @classmethod
    def build(
        cls,
        semantic_stack: SemanticStack,
        most_recent_token: Token | None,
    ) -> "Identifier":
        if most_recent_token is None:
            raise ValueError(
                f"No most recent token found when generating {cls.__name__}",
            )
        if most_recent_token == TokenType.KEYWORD_PRINT:
            value = "print"
        else:
            value = cls.get_token_value(most_recent_token)
        return Identifier(value)

    @override
    def __str__(self):
        return f"Identifier {self.value}"


action_to_astnode: dict[
    SemanticAction,
    Callable[[SemanticStack, Token | None], ASTNode],
] = {
    SemanticAction.MAKE_PROGRAM: Program.build,
    SemanticAction.MAKE_DEFINITION_LIST: DefinitionList.build,
    SemanticAction.MAKE_DEFINITION: Definition.build,
    SemanticAction.MAKE_IDENTIFIER: Identifier.build,
    SemanticAction.MAKE_PARAMETER_LIST: ParameterList.build,
    SemanticAction.MAKE_ID_WITH_TYPE: IdWithType.build,
    SemanticAction.MAKE_INTEGER_TYPE: IntegerType.build,
    SemanticAction.MAKE_BOOLEAN_TYPE: BooleanType.build,
    SemanticAction.MAKE_BODY: Body.build,
    SemanticAction.MAKE_FUNCTION_CALL_EXPRESSION: FunctionCallExpression.build,
    SemanticAction.MAKE_EQUALS_EXPRESSION: EqualsExpression.build,
    SemanticAction.MAKE_LESS_THAN_EXPRESSION: LessThanExpression.build,
    SemanticAction.MAKE_OR_EXPRESSION: OrExpression.build,
    SemanticAction.MAKE_PLUS_EXPRESSION: PlusExpression.build,
    SemanticAction.MAKE_MINUS_EXPRESSION: MinusExpression.build,
    SemanticAction.MAKE_TIMES_EXPRESSION: TimesExpression.build,
    SemanticAction.MAKE_DIVIDE_EXPRESSION: DivideExpression.build,
    SemanticAction.MAKE_AND_EXPRESSION: AndExpression.build,
    SemanticAction.MAKE_NOT_EXPRESSION: NotExpression.build,
    SemanticAction.MAKE_UNARY_MINUS_EXPRESSION: UnaryMinusExpression.build,
    SemanticAction.MAKE_IF_EXPRESSION: IfExpression.build,
    SemanticAction.MAKE_ARGUMENT_LIST: ArgumentList.build,
    SemanticAction.MAKE_ARGUMENT: Argument.build,
    SemanticAction.MAKE_INTEGER_LITERAL: IntegerLiteral.build,
    SemanticAction.MAKE_BOOLEAN_LITERAL: BooleanLiteral.build,
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
        print(f"{sub_indent}name {node.name.value}")
        print(f"{sub_indent}parameters")
        display_astnode(node.parameters, indent + 2, spacer)
        print(f"{sub_indent}returns {node.return_type}")
        print(f"{sub_indent}body")
        display_astnode(node.body, indent + 2, spacer)
    elif isinstance(node, ParameterList):
        for parameter in node.definitions:
            display_astnode(parameter, indent, spacer)
    elif isinstance(node, IdWithType):
        print(f"{main_indent}{node.type} {node.name.value}")
    elif isinstance(node, Body):
        for print_stm in node.print_expressions:
            display_astnode(print_stm, indent, spacer)
        display_astnode(node.body, indent, spacer)
    elif isinstance(node, FunctionCallExpression):
        print(f"{main_indent}function call")
        print(f"{sub_indent}name {node.function_name.value}")
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
    elif isinstance(node, (Identifier, Literal)):
        print(f"{main_indent}{node}")
    elif isinstance(node, IfExpression):
        print(f"{main_indent}{node}")
        print(f"{sub_indent}condition")
        display_astnode(node.condition, indent + 2, spacer)
        print(f"{sub_indent}consequent")
        display_astnode(node.consequent, indent + 2, spacer)
        print(f"{sub_indent}alternative")
        display_astnode(node.alternative, indent + 2, spacer)
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
            f'{key} [label = "{node}\nname {node.name.value}\nreturns {node.return_type}"]',
        )
        link(node, node.parameters, "parameters")
        link(node, node.body, "body")
    elif isinstance(node, ParameterList):
        print(f'{key} [label = "{node}"]')
        for parameter in node.definitions:
            link(node, parameter)
    elif isinstance(node, IdWithType):
        print(f'{key} [label = "name {node.name.value}\ntype {node.type}"]')
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
        print(f'{key} [label = "{node}\n{node.function_name.value}"]')
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
    elif isinstance(node, (Identifier, Literal)):
        print(f'{key} [label = "{node}"]')
    else:
        raise NotImplementedError(f"Node of type {node} has not yet been implemented")
