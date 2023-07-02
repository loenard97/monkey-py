from dataclasses import dataclass
from typing import List
from pymonkey.code.code import Instructions, MOpcode

from pymonkey.evaluator.mobject import MIntegerObject, MObject


STACK_SIZE = 2048


@dataclass
class VM:
    constants: List[MObject]
    instructions: Instructions
    stack: List[MObject]
    stack_pointer: int

    def __init__(self, bytecode) -> None:
        self.instructions = bytecode.instructions
        self.constants = bytecode.constants
        self.stack = []
        self.stack_pointer = 0

    def stack_top(self) -> None | MObject:
        if self.stack_pointer == 0:
            return None
        return self.stack[self.stack_pointer - 1]

    def stack_push(self, obj: MObject) -> None:
        self.stack.append(obj)
        self.stack_pointer += 1

    def stack_pop(self) -> MObject:
        self.stack_pointer -= 1
        return self.stack.pop()

    def run(self):
        for ins in self.instructions:
            op = MOpcode(ins[0])

            if op == MOpcode.OpConstant:
                const_index = int.from_bytes(ins[1:], byteorder='big', signed=False)
                self.stack_push(self.constants[const_index])

            elif op == MOpcode.OpAdd:
                right = self.stack_pop()
                left = self.stack_pop()
                if isinstance(right, MIntegerObject) and isinstance(left, MIntegerObject):
                    result = left.value + right.value
                else:
                    raise TypeError("OpAdd operands not Integers")
                self.stack_push(MIntegerObject(result))

            else:
                raise TypeError("unknown op code")

