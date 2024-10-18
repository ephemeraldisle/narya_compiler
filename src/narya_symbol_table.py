from typing import Dict, Optional, List
from enum import Enum, auto

class ScopeType(Enum):
    GLOBAL = auto()
    RING = auto()
    GROUP = auto()
    FUNCTION = auto()
    CONTROL_FLOW = auto()
    ANONYMOUS = auto()


class ScopeNode:
    def __init__(self, name: str, scope_type: ScopeType, parent: Optional['ScopeNode'] = None, is_dangerous: bool = False):
        self.name = name
        self.scope_type = scope_type
        self.parent = parent
        self.children: List[ScopeNode] = []
        self.symbols: Dict[str, Symbol] = {}
        self.is_dangerous = is_dangerous

    def add_child(self, name: str, scope_type: ScopeType, is_dangerous: bool = False) -> 'ScopeNode':
        child = ScopeNode(name, scope_type, self, is_dangerous)
        self.children.append(child)
        return child


class Symbol:
    def __init__(self, name: str, type: str, kind: str, scope: str):
        self.name = name
        self.type = type
        self.kind = kind
        self.scope = scope
        
class SymbolTable:
    def __init__(self):
        self.root = ScopeNode("global", ScopeType.GLOBAL)
        self.current_scope = self.root
        self.anonymous_counter = 0

    def enter_scope(self, name: str, scope_type: ScopeType, is_dangerous: bool = False):
        if scope_type == ScopeType.RING and self.current_scope.scope_type != ScopeType.GLOBAL:
            raise ValueError("Rings can only be defined at the global level")
        if scope_type == ScopeType.ANONYMOUS:
            self.anonymous_counter += 1
            name = f"anonymous_{self.anonymous_counter}"
        self.current_scope = self.current_scope.add_child(name, scope_type, is_dangerous)

    def exit_scope(self):
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent

    def add_symbol(self, name: str, type: str, kind: str):
        if name in self.current_scope.symbols:
            raise ValueError(f"Symbol '{name}' already defined in current scope")
        self.current_scope.symbols[name] = Symbol(name, type, kind, self.current_scope)

    def lookup_symbol(self, name: str) -> Optional[Symbol]:
        scope = self.current_scope
        while scope:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
        return None

    def is_in_dangerous_scope(self) -> bool:
        scope = self.current_scope
        while scope:
            if scope.is_dangerous:
                return True
            scope = scope.parent
        return False
