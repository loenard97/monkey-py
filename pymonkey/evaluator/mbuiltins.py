from typing import List

from pymonkey.evaluator.mobject import (
    MArrayObject,
    MBuiltinFunction,
    MErrorObject,
    MIntegerObject,
    MObject,
    MStringObject,
)


class Builtins:
    def __init__(self):
        self.fns = {
            "len": MBuiltinFunction(self.len),
            "puts": MBuiltinFunction(self.puts),
        }

    def len(self, args: List[MObject]):
        if len(args) != 1:
            return MErrorObject("len needs exactly one argument")

        if isinstance(args[0], MStringObject) or isinstance(args[0], MArrayObject):
            return MIntegerObject(len(args[0].value))

        return MErrorObject("len unknown expression")

    def puts(self, args: List[MObject]):
        print(*args)
