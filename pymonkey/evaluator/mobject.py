from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Union

from pymonkey.parser.mast import MBlockStatement, MExpression


class MObject(ABC):
    @abstractmethod
    def __str__(self):
        return NotImplementedError


class MValuedObject(MObject, ABC):
    value: int | bool | str


@dataclass
class MNullObject(MObject):
    @classmethod
    def __str__(cls):
        return "None"


@dataclass
class MIntegerObject(MValuedObject):
    value: int

    def __str__(self):
        return f"{self.value}"


@dataclass
class MBooleanObject(MValuedObject):
    value: bool

    def __str__(self):
        return f"{self.value}".lower()


@dataclass
class MStringObject(MValuedObject):
    value: str

    def __str__(self):
        return f"{self.value}"


@dataclass
class MReturnValueObject(MObject):
    value: MObject

    def __str__(self):
        return f"{self.value}"


@dataclass
class MErrorObject(MObject):
    message: str

    def __str__(self):
        return f"ERROR: {self.message}"


@dataclass
class MFunctionObject(MObject):
    parameters: List[MExpression]
    body: MBlockStatement
    env: "MEnvironment"

    def __str__(self):
        params = ", ".join([str(p) for p in self.parameters])
        return f"fn ({params}) {{ {self.body} }}"


@dataclass
class MEnvironment:
    store: dict
    outer: Union["MEnvironment", None]

    def __init__(self):
        self.store = {}
        self.outer = None

    def __str__(self):
        return f"Environment <{self.store}>"

    @classmethod
    def new_enclosed(cls, outer: "MEnvironment") -> "MEnvironment":
        ret = cls()
        ret.outer = outer
        return ret

    def set(self, name: str, val: MObject):
        self.store[name] = val
        return val

    def get(self, name: str) -> MObject:
        return self.store[name]


@dataclass
class MBuiltinFunction(MObject):
    fn: Callable

    def __str__(self):
        return "fn.__name__"


@dataclass
class MArrayObject(MObject):
    value: List[MObject]

    def __str__(self):
        vals = ", ".join([str(e) for e in self.value])
        return f"[{vals}]"
