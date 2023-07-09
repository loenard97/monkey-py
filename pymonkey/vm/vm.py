from dataclasses import dataclass
from typing import List

from pymonkey.code.code import Instructions, MOpcode
from pymonkey.compiler.compiler import Bytecode
from pymonkey.evaluator.mobject import (
    MArrayObject,
    MBooleanObject,
    MHashMapObject,
    MIntegerObject,
    MNullObject,
    MObject,
    MStringObject,
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
    globals: dict[int, MObject]

    def __init__(self, bytecode: Bytecode) -> None:
        self.instructions = bytecode.instructions
        self.constants = bytecode.constants
        self.stack = []
        self.stack_pointer = 0
        self.last_pop = MNullObject()
        self.globals = {}

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

            elif op == MOpcode.OpSetGlobal:
                global_index = int.from_bytes(ins[1:], byteorder="big", signed=False)
                self.globals[global_index] = self.stack_pop()

            elif op == MOpcode.OpGetGlobal:
                global_index = int.from_bytes(ins[1:], byteorder="big", signed=False)
                self.stack_push(self.globals[global_index])

            elif op == MOpcode.OpArray:
                num_elements_array = int.from_bytes(
                    ins[1:], byteorder="big", signed=False
                )
                arr = self.build_array(
                    self.stack_pointer - num_elements_array, self.stack_pointer
                )
                self.stack_pointer -= num_elements_array
                self.stack_push(arr)

            elif op == MOpcode.OpHash:
                num_elements_hash = int.from_bytes(
                    ins[1:], byteorder="big", signed=False
                )
                hashmap = self.build_hashmap(
                    self.stack_pointer - num_elements_hash, self.stack_pointer
                )
                self.stack_pointer -= num_elements_hash
                self.stack_push(hashmap)

            elif op == MOpcode.OpIndex:
                index = self.stack_pop()
                left = self.stack_pop()
                self.execute_index_expression(left, index)

            else:
                raise TypeError("unknown op code")

            ip += 1

    def execute_binary_operation(self, op: MOpcode) -> None:
        right = self.stack_pop()
        left = self.stack_pop()

        if isinstance(right, MIntegerObject) and isinstance(left, MIntegerObject):
            result_int = 0
            if op == MOpcode.OpAdd:
                result_int = left.value + right.value
            elif op == MOpcode.OpSub:
                result_int = left.value - right.value
            elif op == MOpcode.OpMul:
                result_int = left.value * right.value
            elif op == MOpcode.OpDiv:
                result_int = left.value // right.value
            else:
                raise TypeError("unsupported operation for types")
            self.stack_push(MIntegerObject(result_int))

        elif isinstance(right, MStringObject) and isinstance(left, MStringObject):
            result_str = ""
            if op == MOpcode.OpAdd:
                result_str = left.value + right.value
            else:
                raise TypeError("unsupported operation for types")
            self.stack_push(MStringObject(result_str))

        else:
            raise TypeError("OpAdd operands not Integers")

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

    def execute_index_expression(self, left: MObject, index: MObject) -> None:
        if isinstance(left, MArrayObject) and isinstance(index, MIntegerObject):
            self.stack_push(left.value[index.value])
        elif isinstance(left, MHashMapObject) and isinstance(index, MValuedObject):
            self.stack_push(left.value[index])
        else:
            raise TypeError("cant apply index")

    def build_array(self, start_index: int, end_index: int) -> MObject:
        elem = []
        for i in range(start_index, end_index):
            elem.append(self.stack[i])
        return MArrayObject(elem)

    def build_hashmap(self, start_index: int, end_index: int) -> MObject:
        hashmap: dict[MValuedObject, MObject] = {}
        for i in range(start_index, end_index, 2):
            key = self.stack[i]
            if not isinstance(key, MValuedObject):
                raise TypeError("hashmap key not hashable")
            value = self.stack[i + 1]
            hashmap[key] = value
        return MHashMapObject(hashmap)
