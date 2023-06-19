from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from pymonkey.ast import BlockStatement, Expression, Identifier


ObjectType = str

NULL_OBJ = "NULL"
ERROR_OBJ = "ERROR"

INTEGER_OBJ = "INTEGER"
BOOLEAN_OBJ = "BOOLEAN"

RETURN_VALUE_OBJ = "RETURN_VALUE"
FUNCTION_OBJ = "FUNCTION"


class IObject(ABC):

    type: ObjectType

    @abstractmethod
    def __str__(self):
        return NotImplementedError


class ValuedObject(IObject, ABC):

    value: int | bool


@dataclass
class NullObject(IObject):

    @classmethod
    def __str__(cls):
        return f"None"


@dataclass
class IntegerObject(ValuedObject):

    value: int
    type = INTEGER_OBJ

    def __str__(self):
        return f"{self.value}"


@dataclass
class BooleanObject(ValuedObject):

    value: bool
    type = BOOLEAN_OBJ

    def __str__(self):
        return f"{self.value}".lower()


@dataclass
class ReturnValueObject(IObject):

    value: IObject
    type = RETURN_VALUE_OBJ

    def __str__(self):
        return f"{self.value}"


@dataclass
class ErrorObject(IObject):

    message: str
    type = ERROR_OBJ

    def __str__(self):
        return f"ERROR: {self.message}"


@dataclass
class FunctionObject(IObject):

    parameters: List[Expression]
    body: BlockStatement
    env: "Environment"
    type = FUNCTION_OBJ

    def __str__(self):
        params = ', '.join([str(p) for p in self.parameters])
        return f"fn ({params}) {{ {self.body} }}"

@dataclass
class Environment:

    store: dict
    outer: "Environment" | None

    def __init__(self):
        self.store = {}
        self.outer = None

    @classmethod
    def new_enclosed(cls, outer: "Environment") -> "Environment":
        ret = cls()
        ret.outer = outer
        return ret

    def set(self, name: str, val: IObject):
        self.store[name] = val
        return val

    def get(self, name: str) -> IObject:
        return self.store[name]

