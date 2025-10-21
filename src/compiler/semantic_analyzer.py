from ast import Expression

from compiler.ast import (
    Definition,
    ParameterList,
    Program,
)
from compiler.symbol_table import SymbolTable


class SemanticAnalyzer:
    def __init__(self, ast: Program):
        self.ast: Program = ast
        self.symbol_table: SymbolTable = SymbolTable()

    def analyze(self) -> None:
        self._program_resolve(self.ast)

    def _program_resolve(self, program: Program) -> None:
        raise NotImplementedError

    def _definition_resolve(self, definition: Definition) -> None:
        raise NotImplementedError

    def _parameter_list_resolve(self, parameter_list: ParameterList) -> None:
        raise NotImplementedError

    def _expression_resolve(self, expression: Expression) -> None:
        raise NotImplementedError
