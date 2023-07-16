from dataclasses import dataclass
from enum import Enum, auto


class SymbolScope(Enum):
    Global = auto()
    Local = auto()


@dataclass
class Symbol:
    name: str
    scope: SymbolScope
    index: int


@dataclass
class SymbolTable:
    outer: "None | SymbolTable"
    store: dict[str, Symbol]
    num_definitions: int

    def __init__(self, outer: "None | SymbolTable" = None) -> None:
        self.outer = outer
        self.store = {}
        self.num_definitions = 0

    @classmethod
    def new_enclosed(cls, outer: "SymbolTable") -> "SymbolTable":
        return SymbolTable(outer=outer)

    def define(self, name: str) -> Symbol:
        if self.outer is None:
            symbol = Symbol(name, SymbolScope.Global, self.num_definitions)
        else:
            symbol = Symbol(name, SymbolScope.Local, self.num_definitions)

        self.store[name] = symbol
        self.num_definitions += 1
        return symbol

    def resolve(self, name: str) -> None | Symbol:
        obj = self.store.get(name)
        if obj is None and self.outer is not None:
            return self.outer.resolve(name)
        return obj
