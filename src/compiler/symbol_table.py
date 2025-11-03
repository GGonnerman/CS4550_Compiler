from enum import Enum, auto

from typing_extensions import override

from compiler.ast_nodes import AnnotationType


class Kind(Enum):
    LOCAL = auto()
    PARAM = auto()
    GLOBAL = auto()


class Symbol:
    def __init__(
        self,
        name: str,
        kind: Kind,
        symbol_type: AnnotationType,
        parameters: "list[Symbol] | None" = None,
    ):
        self.name: str = name
        self.kind: Kind = kind
        self.symbol_type: AnnotationType = symbol_type
        self.forward_references: set[str] = set()
        self.backward_references: set[str] = set()
        self.parameters: list[Symbol] | None = parameters

    def add_forward_reference(self, function_name: str):
        self.forward_references.add(function_name)

    def add_backward_reference(self, function_name: str):
        self.backward_references.add(function_name)

    @override
    def __str__(self) -> str:
        out = [
            f"{self.name}",
            f"\tsymbol_type = {self.symbol_type}",
        ]
        if self.parameters is not None and len(self.parameters) > 0:
            out.append(
                "\tparameters = "
                + ", ".join(
                    f"{parameter.name}: {parameter.symbol_type}"
                    for parameter in self.parameters
                ),
            )
        if len(self.forward_references) > 0:
            out.append(f"\tfunctions it calls = {', '.join(self.forward_references)}")
        if len(self.backward_references) > 0:
            out.append(
                f"\tfunctions that call it = {', '.join(self.backward_references)}"
            )
        return "\n".join(out)


class SymbolTable:
    def __init__(self):
        self._scope_stack: list[dict[str, Symbol]] = [{}]

    def __iter__(self):
        for scope in self._scope_stack:
            for symbol in scope.values():
                yield symbol

    def at(self, scope: int):
        return self._scope_stack[scope]

    def update_backward_references(self):
        for symbol in self:
            for called_function_name in symbol.forward_references:
                called_function = self.scope_lookup(called_function_name)
                if called_function is None:
                    raise ValueError(
                        f"Trying to update backreference from {symbol.name} to non-existant function {called_function_name}",
                    )
                called_function.add_backward_reference(
                    symbol.name,
                )

    def scope_enter(self) -> None:
        self._scope_stack.append({})

    def scope_exit(self) -> None:
        _ = self._scope_stack.pop()

    @property
    def scope_level(self) -> int:
        return len(self._scope_stack)

    def scope_bind(self, name: str, symbol: Symbol) -> None:
        if self.scope_lookup_current(name):
            raise KeyError(f"Duplicated symbol {name} in scope {self._scope_stack[-1]}")
        self._scope_stack[-1][name] = symbol

    def scope_lookup(self, name: str) -> Symbol | None:
        for scope in reversed(self._scope_stack):
            if name in scope:
                return scope[name]
        return None

    def scope_lookup_current(self, name: str) -> Symbol | None:
        current_scope = self._scope_stack[-1]
        if name in current_scope:
            return current_scope[name]
        return None

    @override
    def __str__(self) -> str:
        out: list[str] = []
        for idx, scope in enumerate(self._scope_stack):
            if idx != 0:
                out.append("")
            for value in scope.values():
                out.append(str(value))
        return "\n".join(out)
