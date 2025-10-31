from enum import Enum, auto

from typing_extensions import override

from compiler.ast_nodes import AnnotationType


class Kind(Enum):
    LOCAL = auto()
    PARAM = auto()
    GLOBAL = auto()


class Symbol:
    def __init__(self, name: str, kind: Kind, symbol_type: AnnotationType):
        self.name: str = name
        self.kind: Kind = kind
        self.symbol_type: AnnotationType = symbol_type
        self.forward_references: set[str] = set()
        self.backward_references: set[str] = set()

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
        if len(self.forward_references) > 0:
            out.append(f"\tforward_refs = {', '.join(self.forward_references)}")
        if len(self.backward_references) > 0:
            out.append(f"\tbackward_refs = {', '.join(self.backward_references)}")
        return "\n".join(out)


class SymbolTable:
    def __init__(self):
        self._scope_stack: list[dict[str, Symbol]] = [{}]

    def update_backward_references(self):
        for symbol in self._scope_stack[0].values():
            for called_function_name in symbol.forward_references:
                self._scope_stack[0][called_function_name].add_backward_reference(
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
        for scope in self._scope_stack:
            out.append("")
            for value in scope.values():
                out.append(str(value))
        return "\n".join(out)
