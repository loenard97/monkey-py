from dataclasses import dataclass
from typing import List

from pymonkey.code.code import Instructions, MOpcode
from pymonkey.compiler.compiler import Bytecode
from pymonkey.evaluator.mobject import (
    MBooleanObject,
    MIntegerObject,
    MNullObject,
    MObject,
)


@dataclass
class VM:
    constants: List[MObject]
    instructions: Instructions
    stack: List[MObject]
    stack_pointer: int
    last_pop: MObject

    def __init__(self, bytecode: Bytecode) -> None:
        self.instructions = bytecode.instructions
        self.constants = bytecode.constants
        self.stack = []
        self.stack_pointer = 0
        self.last_pop = MNullObject()

    def stack_top(self) -> None | MObject:
        if self.stack_pointer == 0:
            return None
        return self.stack[self.stack_pointer - 1]

    def stack_push(self, obj: MObject) -> None:
        self.stack.append(obj)
        self.stack_pointer += 1

    def stack_pop(self) -> MObject:
        self.stack_pointer -= 1
        self.last_pop = self.stack.pop()
        return self.last_pop

    def run(self) -> None:
        for ins in self.instructions:
            op = MOpcode(ins[0])

            if op == MOpcode.OpConstant:
                const_index = int.from_bytes(ins[1:], byteorder="big", signed=False)
                self.stack_push(self.constants[const_index])

            elif (
                op == MOpcode.OpAdd
                or op == MOpcode.OpSub
                or op == MOpcode.OpMul
                or op == MOpcode.OpDiv
            ):
                self.execute_binary_operation(op)

            elif op == MOpcode.OpPop:
                self.stack_pop()

            elif op == MOpcode.OpTrue:
                self.stack_push(MBooleanObject(True))

            elif op == MOpcode.OpFalse:
                self.stack_push(MBooleanObject(False))

            else:
                raise TypeError("unknown op code")

    def execute_binary_operation(self, op: MOpcode) -> None:
        right = self.stack_pop()
        left = self.stack_pop()
        if not (isinstance(right, MIntegerObject) and isinstance(left, MIntegerObject)):
            raise TypeError("OpAdd operands not Integers")

        result = 0
        if op == MOpcode.OpAdd:
            result = left.value + right.value
        elif op == MOpcode.OpSub:
            result = left.value - right.value
        elif op == MOpcode.OpMul:
            result = left.value * right.value
        elif op == MOpcode.OpDiv:
            result = left.value // right.value
        self.stack_push(MIntegerObject(result))
