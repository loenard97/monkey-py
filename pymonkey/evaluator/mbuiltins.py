from typing import List

from pymonkey.evaluator.mobject import (
    MBuiltinFunction,
    MErrorObject,
    MIntegerObject,
    MStringObject,
)


class Builtins:
    def __init__(self):
        self.fns = {
            "len": MBuiltinFunction(self.len),
        }

    def len(self, args: List[MStringObject]):
        if len(args) == 1 and isinstance(args[0], MStringObject):
            return MIntegerObject(len(args[0].value))
        return MErrorObject("len needs 1 String arg")
