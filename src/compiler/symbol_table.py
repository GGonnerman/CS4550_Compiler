from enum import Enum, auto


class Kind(Enum):
    LOCAL = auto()
    PARAM = auto()
    GLOBAL = auto()


class PrimitiveType(Enum):
    BOOLEAN = auto()
    INTEGER = auto()
    FUNCTION = auto()


class Symbol:
    def __init__(self, name: str, kind: Kind, symbol_type: PrimitiveType):
        self.name: str = name
        self.kind: Kind = kind
        self.symbol_type: PrimitiveType = symbol_type


class SymbolTable:
    def __init__(self):
        self._scope_stack: list[dict[str, Symbol]] = [{}]

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
