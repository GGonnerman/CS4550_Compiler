from dataclasses import dataclass
from enum import Enum, auto

from compiler.ast_nodes import (
    AndExpression,
    Argument,
    ArgumentList,
    ASTNode,
    Body,
    BooleanAnnotation,
    BooleanLiteral,
    BooleanType,
    Definition,
    DefinitionList,
    DivideExpression,
    EmptyAnnotation,
    EqualsExpression,
    ErrorAnnotation,
    FunctionAnnotation,
    FunctionCallExpression,
    Identifier,
    IdWithType,
    IfExpression,
    IntegerAnnotation,
    IntegerLiteral,
    IntegerType,
    LessThanExpression,
    MinusExpression,
    NotExpression,
    OrExpression,
    ParameterList,
    PlusExpression,
    Program,
    SequenceAnnotation,
    TimesExpression,
    Type,
    UnaryMinusExpression,
    UnionAnnotation,
    display_astnode,
)
from compiler.klein_errors import SemanticError
from compiler.parser import Parser
from compiler.scanner import Scanner
from compiler.symbol_table import Kind, Symbol, SymbolTable


class IssueType(Enum):
    ERROR = auto()
    WARNING = auto()


@dataclass
class Context:
    function: Symbol
    parameters: set[str]
    used_parameters: set[str]


class SemanticAnalyzer:
    def __init__(self, ast: Program):
        self.ast: Program = ast
        self.symbol_table: SymbolTable = SymbolTable()
        self.issues: list[tuple[IssueType, str]] = []
        self._context: Context | None = None
        self._printable_context: str | None = None

    @property
    def error_count(self):
        return len([issue for issue in self.issues if issue[0] == IssueType.ERROR])

    @property
    def warning_count(self):
        return len([issue for issue in self.issues if issue[0] == IssueType.WARNING])

    def _type_to_annotatiton(
        self,
        my_type: Type,
    ) -> IntegerAnnotation | BooleanAnnotation:
        return (
            IntegerAnnotation()
            if isinstance(my_type, IntegerType)
            else BooleanAnnotation()
        )

    def annotate(self):
        self._create_shallow_symbol_table()
        self._annotate(self.ast)
        self.symbol_table.update_backward_references()
        self._check_function_warnings()
        if self.error_count > 0:
            is_plural = self.error_count > 1
            raise SemanticError(
                f"Encountered {self.error_count} error{'s' if is_plural else ''} when analyzing ast",
            )

    def display_issues(self):
        for issue_type, issue in self.issues:
            issue_title = "Warning" if issue_type == IssueType.WARNING else "Error"
            print(f"Klein Semantic {issue_title}: {issue}")

    def _check_function_warnings(self):
        for symbol in self.symbol_table:
            if symbol.name in ("main", "print"):
                continue
            if len(symbol.backward_references) == 0:
                self._add_warning(f"Unused function {symbol.name}")

    def _add_error(self, error_message: str):
        self.issues.append((IssueType.ERROR, error_message))

    def _add_warning(self, warning_message: str):
        self.issues.append((IssueType.WARNING, warning_message))

    def _create_shallow_symbol_table(self):
        self.symbol_table.scope_bind(
            "print",
            Symbol(
                "print",
                Kind.GLOBAL,
                FunctionAnnotation(
                    SequenceAnnotation(
                        [UnionAnnotation((IntegerAnnotation(), BooleanAnnotation()))],
                    ),
                    EmptyAnnotation(),
                ),
            ),
        )
        seen_function_names: set[str] = set()
        for definition in self.ast.definition_list:
            if definition.name.value in seen_function_names:
                self._add_error(f"Duplicated function name {definition.name.value}")
                continue
            seen_function_names.add(definition.name.value)
            parameter_symbols: list[Symbol] = [
                Symbol(
                    parameter.name.value,
                    Kind.PARAM,
                    self._type_to_annotatiton(parameter.type),
                )
                for parameter in definition.parameters
            ]
            param_annotation = SequenceAnnotation(
                [parameter.symbol_type for parameter in parameter_symbols],
            )
            return_annotation = self._type_to_annotatiton(definition.return_type)
            self.symbol_table.scope_bind(
                definition.name.value,
                Symbol(
                    definition.name.value,
                    Kind.GLOBAL,
                    FunctionAnnotation(param_annotation, return_annotation),
                    parameter_symbols,
                ),
            )
        if "main" not in seen_function_names:
            self._add_error("Missing a main function")

    def _annotate(self, node: ASTNode):
        if isinstance(node, Program):
            self._annotate(node.definition_list)
        elif isinstance(node, DefinitionList):
            for definition in node:
                self._annotate(definition)
        elif isinstance(node, Definition):
            current_function = self.symbol_table.scope_lookup(node.name.value)
            if current_function is None:
                raise ValueError(f"Inside of unbound function {node.name.value}")
            self._printable_context = f"Function {node.name.value}: "
            self.symbol_table.scope_enter()  # Enter parameter scope
            self._annotate(node.parameters)
            self._annotate(node.return_type)
            # Annotate body and check for mismatch
            self.symbol_table.scope_enter()  # Enter body scope
            self._context = Context(
                current_function,
                set(parameter.name.value for parameter in node.parameters),
                set(),
            )
            self._annotate(node.body)
            # Checking for unused parameters
            for parameter in self._context.parameters - self._context.used_parameters:
                self._add_warning(
                    f"{self._printable_context}Unused parameter {parameter}",
                )
            self.symbol_table.scope_exit()  # Exit body and parameter scope
            self.symbol_table.scope_exit()
            node.add_annotation(
                FunctionAnnotation(
                    node.parameters.annotation,
                    node.return_type.annotation,
                ),
            )
            if node.body.annotation != node.return_type.annotation:
                self._add_error(
                    f"Expected function {node.name.value} to return {node.return_type.annotation} instead found {node.body.annotation}",
                )
        elif isinstance(node, ParameterList):
            seen_parameter_names: set[str] = set()
            for parameter in node:
                self._annotate(parameter)
                if parameter.name.value in seen_parameter_names:
                    self._add_error(
                        f"{self._printable_context}Duplicated parameter name {parameter.name.value}",
                    )
                    continue
                seen_parameter_names.add(parameter.name.value)
                self.symbol_table.scope_bind(
                    parameter.name.value,
                    Symbol(parameter.name.value, Kind.PARAM, parameter.annotation),
                )
            annotation = SequenceAnnotation([param.annotation for param in node])
            node.add_annotation(annotation)

        elif isinstance(node, IdWithType):
            self._annotate(node.type)
            node.add_annotation(node.type.annotation)
        elif isinstance(node, (IntegerType, IntegerLiteral)):
            node.add_annotation(IntegerAnnotation())
        elif isinstance(node, (BooleanType, BooleanLiteral)):
            node.add_annotation(BooleanAnnotation())
        elif isinstance(node, Identifier):
            annotation_type: Symbol | None = self.symbol_table.scope_lookup(node.value)
            if annotation_type is None:
                self._add_error(
                    f"{self._printable_context}Missing identifier {node.value} referenced",
                )
                node.add_annotation(ErrorAnnotation())
                return
            symbol_type = annotation_type.symbol_type
            if isinstance(symbol_type, FunctionAnnotation):
                self._add_error(
                    f"{self._printable_context}Attempted to use function {annotation_type.name} as identifier",
                )
                node.add_annotation(ErrorAnnotation())
                return
            if self._context is None:
                # This code *should* be unreachable
                raise ValueError("Referenced identifier without being in a context")
            self._context.used_parameters.add(node.value)
            node.add_annotation(annotation_type.symbol_type)
        elif isinstance(node, FunctionCallExpression):
            self._annotate(node.argument_list)
            symbol: Symbol | None = self.symbol_table.scope_lookup(
                node.function_name.value,
            )
            if symbol is None:
                node.add_annotation(ErrorAnnotation())
                self._add_error(
                    f"{self._printable_context}Attempted to call non-existant function {node.function_name.value}",
                )
                return
            symbol_type = symbol.symbol_type
            if not isinstance(symbol_type, FunctionAnnotation):
                node.add_annotation(ErrorAnnotation())
                self._add_error(
                    f"{self._printable_context}Attempted to call parameter {node.function_name.value} as a function",
                )
                return
            if self._context is None:
                # This code *should* be unreachable
                raise ValueError("Called a function without being in a context")
            self._context.function.add_forward_reference(symbol.name)
            passed_arguments = node.argument_list.annotation
            expected_arguments = symbol_type.source
            if passed_arguments != expected_arguments:
                node.add_annotation(ErrorAnnotation())
                if not isinstance(
                    passed_arguments,
                    SequenceAnnotation,
                ) or not isinstance(expected_arguments, SequenceAnnotation):
                    self._add_error(
                        f"{self._printable_context}Wrong argument passed to {node.function_name.value}",
                    )
                    return
                if len(passed_arguments) > len(expected_arguments):
                    self._add_error(
                        f"{self._printable_context}Too many arguments passed to {node.function_name.value}. Expected {len(expected_arguments)} and receieved {len(passed_arguments)}",
                    )
                elif len(passed_arguments) < len(expected_arguments):
                    self._add_error(
                        f"{self._printable_context}Too few arguments passed to {node.function_name.value}. Expected {len(expected_arguments)} and receieved {len(passed_arguments)}",
                    )
                else:
                    self._add_error(
                        f"{self._printable_context}Mismatched argument types passed to {node.function_name.value}. Expected {expected_arguments} and received {passed_arguments}",
                    )
                return
            node.add_annotation(
                symbol_type.destination,
            )
        elif isinstance(
            node,
            (PlusExpression, MinusExpression, TimesExpression, DivideExpression),
        ):
            self._annotate(node.left_side)
            self._annotate(node.right_side)
            if node.left_side.annotation != IntegerAnnotation():
                self._add_error(
                    f"{self._printable_context}Expected left side of {node} to be Integer instead found {node.left_side.annotation}",
                )
                node.add_annotation(ErrorAnnotation())
                return
            if node.right_side.annotation != IntegerAnnotation():
                self._add_error(
                    f"{self._printable_context}Expected right side of {node} to be Integer instead found {node.right_side.annotation}",
                )
                node.add_annotation(ErrorAnnotation())
                return
            node.add_annotation(IntegerAnnotation())
        elif isinstance(
            node,
            (LessThanExpression),
        ):
            self._annotate(node.left_side)
            self._annotate(node.right_side)
            if node.left_side.annotation != IntegerAnnotation():
                self._add_error(
                    f"{self._printable_context}Expected left side of {node} to be Integer instead found {node.left_side.annotation}",
                )
                node.add_annotation(ErrorAnnotation())
                return
            if node.right_side.annotation != IntegerAnnotation():
                self._add_error(
                    f"{self._printable_context}Expected right side of {node} to be Integer instead found {node.right_side.annotation}",
                )
                node.add_annotation(ErrorAnnotation())
                return
            node.add_annotation(BooleanAnnotation())
        elif isinstance(
            node,
            (AndExpression, OrExpression),
        ):
            self._annotate(node.left_side)
            self._annotate(node.right_side)
            if node.left_side.annotation != BooleanAnnotation():
                self._add_error(
                    f"{self._printable_context}Expected left side of {node} to be Boolean instead found {node.left_side.annotation}",
                )
                node.add_annotation(ErrorAnnotation())
                return
            if node.right_side.annotation != BooleanAnnotation():
                self._add_error(
                    f"{self._printable_context}Expected right side of {node} to be Boolean instead found {node.right_side.annotation}",
                )
                node.add_annotation(ErrorAnnotation())
                return
            node.add_annotation(BooleanAnnotation())
        elif isinstance(
            node,
            (EqualsExpression),
        ):
            self._annotate(node.left_side)
            self._annotate(node.right_side)
            # FIXME: This 99% has errors when mismatch between like unions or whatnot
            if (
                node.left_side.annotation == ErrorAnnotation()
                or node.right_side.annotation == ErrorAnnotation()
            ):
                node.add_annotation(ErrorAnnotation())
                return
            node.add_annotation(BooleanAnnotation())
        elif isinstance(
            node,
            (UnaryMinusExpression),
        ):
            self._annotate(node.value)
            if node.value.annotation != IntegerAnnotation():
                self._add_error(
                    f"{self._printable_context}Expected value of {node} to be Integer instead found {node.value.annotation}",
                )
                node.add_annotation(ErrorAnnotation())
                return
            node.add_annotation(IntegerAnnotation())
        elif isinstance(
            node,
            (NotExpression),
        ):
            self._annotate(node.value)
            if node.value.annotation != BooleanAnnotation():
                self._add_error(
                    f"{self._printable_context}Expected value of {node} to be Boolean instead found {node.value.annotation}",
                )
                node.add_annotation(ErrorAnnotation())
                return
            node.add_annotation(BooleanAnnotation())
        elif isinstance(node, ArgumentList):
            for argument in node.arguments:
                self._annotate(argument)
            node.add_annotation(
                SequenceAnnotation([arg.annotation for arg in node.arguments]),
            )
        elif isinstance(node, IfExpression):
            self._annotate(node.condition)
            self._annotate(node.consequent)
            self._annotate(node.alternative)
            if node.condition.annotation != BooleanAnnotation():
                self._add_error(
                    f"{self._printable_context}Expected condition of {node} to be Boolean instead found {node.condition.annotation}",
                )
                node.add_annotation(ErrorAnnotation())
                return
            if node.consequent.annotation == node.alternative.annotation:
                node.add_annotation(node.consequent.annotation)
            else:
                node.add_annotation(
                    UnionAnnotation(
                        (node.consequent.annotation, node.alternative.annotation),
                    ),
                )
        elif isinstance(node, Argument):
            self._annotate(node.value)
            node.add_annotation(node.value.annotation)
        elif isinstance(node, Body):
            for print_expression in node.print_expressions:
                self._annotate(print_expression)
            self._annotate(node.body)
            node.add_annotation(node.body.annotation)
        else:
            raise NotImplementedError(
                f"Annotating nodes of type {node.__class__.__name__} has not been implemented yet",
            )

    # def analyze(self) -> None:
    #    self._program_resolve(self.ast)

    # def _program_resolve(self, program: Program) -> None:
    #    raise NotImplementedError

    # def _definition_resolve(self, definition: Definition) -> None:
    #    raise NotImplementedError

    # def _parameter_list_resolve(self, parameter_list: ParameterList) -> None:
    #    raise NotImplementedError

    # def _expression_resolve(self, expression: Expression) -> None:
    #    raise NotImplementedError


if __name__ == "__main__":
    with open("programs/semantic-errors.kln") as infile:
        scanner = Scanner(infile.read())
    # scanner = Scanner("""
    # function main(): integer
    #  print(true)
    #  1
    # """)

    parser = Parser(scanner)

    ast = parser.parse()

    sa = SemanticAnalyzer(ast)
    sa.annotate()
    display_astnode(ast)
    print()
    print(str(sa.symbol_table))
