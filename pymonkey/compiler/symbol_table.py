from dataclasses import dataclass
from enum import Enum, auto


class SymbolScope(Enum):
    Global = auto()


@dataclass
class Symbol:
    name: str
    scope: SymbolScope
    index: int


@dataclass
class SymbolTable:
    store: dict[str, Symbol]
    num_definitions: int

    def __init__(self) -> None:
        self.store = {}
        self.num_definitions = 0

    def define(self, name: str) -> Symbol:
        symbol = Symbol(name, SymbolScope.Global, self.num_definitions)
        self.store[name] = symbol
        self.num_definitions += 1
        return symbol

    def resolve(self, name: str) -> None | Symbol:
        return self.store.get(name)
