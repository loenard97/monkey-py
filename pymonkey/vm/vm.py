from dataclasses import dataclass
from typing import List

from pymonkey.code.code import Instructions, MOpcode
from pymonkey.compiler.compiler import Bytecode
from pymonkey.evaluator.mobject import (
    MBooleanObject,
    MIntegerObject,
    MNullObject,
    MObject,
    MValuedObject,
)
from pymonkey.util import flog


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

    @flog
    def run(self) -> None:
        ip = 0
        while ip < len(self.instructions):
            ins = self.instructions[ip]
            if isinstance(ins, list):
                return
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

            elif (
                op == MOpcode.OpGreater
                or op == MOpcode.OpEqual
                or op == MOpcode.OpNotEqual
            ):
                self.execute_comparison(op)

            elif op == MOpcode.OpBang:
                operand = self.stack_pop()
                if isinstance(operand, MBooleanObject):
                    self.stack_push(MBooleanObject(not operand.value))
                if isinstance(operand, MNullObject):
                    self.stack_push(MBooleanObject(True))
                else:
                    self.stack_push(MBooleanObject(False))

            elif op == MOpcode.OpMinus:
                operand = self.stack_pop()
                if isinstance(operand, MIntegerObject):
                    self.stack_push(MIntegerObject(-operand.value))

            elif op == MOpcode.OpJump:
                pos = int.from_bytes(ins[1:], byteorder="big", signed=False)
                ip = pos - 1

            elif op == MOpcode.OpJumpNotTruthy:
                pos = int.from_bytes(ins[1:], byteorder="big", signed=False)
                condition = self.stack_pop()
                if isinstance(condition, MBooleanObject) and not condition.value:
                    ip = pos - 1

            elif op == MOpcode.OpNull:
                self.stack_push(MNullObject())

            else:
                raise TypeError("unknown op code")

            ip += 1

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

    def execute_comparison(self, op: MOpcode) -> None:
        right = self.stack_pop()
        left = self.stack_pop()

        print(type(right), right)
        print(type(left), left)
        print(isinstance(right, MValuedObject))
        print(isinstance(left, MValuedObject))
        print(hasattr(right, "__lt__"))

        if (
            isinstance(right, MValuedObject)
            and isinstance(left, MValuedObject)
            and hasattr(right.value, "__lt__")
        ):
            if op == MOpcode.OpEqual:
                self.stack_push(MBooleanObject(right.value == left.value))

            elif op == MOpcode.OpNotEqual:
                self.stack_push(MBooleanObject(right.value != left.value))

            elif op == MOpcode.OpGreater:
                self.stack_push(MBooleanObject(right.value < left.value))

        else:
            raise ValueError
