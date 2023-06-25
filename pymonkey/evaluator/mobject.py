from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Union

from pymonkey.parser.mast import MBlockStatement, MExpression

ObjectType = str

NULL_OBJ = "NULL"
ERROR_OBJ = "ERROR"

INTEGER_OBJ = "INTEGER"
BOOLEAN_OBJ = "BOOLEAN"
STRING_OBJ = "STRING"

RETURN_VALUE_OBJ = "RETURN_VALUE"
FUNCTION_OBJ = "FUNCTION"
BUILTIN_FN = "BUILTIIN_FN"


class MObject(ABC):
    type: ObjectType

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
    type = INTEGER_OBJ

    def __str__(self):
        return f"{self.value}"


@dataclass
class MBooleanObject(MValuedObject):
    value: bool
    type = BOOLEAN_OBJ

    def __str__(self):
        return f"{self.value}".lower()


@dataclass
class MStringObject(MValuedObject):
    value: str
    type = STRING_OBJ

    def __str__(self):
        return f"{self.value}"


@dataclass
class MReturnValueObject(MObject):
    value: MObject
    type = RETURN_VALUE_OBJ

    def __str__(self):
        return f"{self.value}"


@dataclass
class MErrorObject(MObject):
    message: str
    type = ERROR_OBJ

    def __str__(self):
        return f"ERROR: {self.message}"


@dataclass
class MFunctionObject(MObject):
    parameters: List[MExpression]
    body: MBlockStatement
    env: "MEnvironment"
    type = FUNCTION_OBJ

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
    type = BUILTIN_FN

    def __str__(self):
        return "fn.__name__"
