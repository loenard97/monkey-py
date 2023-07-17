import pickle
from dataclasses import dataclass
from typing import List, Self

from pymonkey.code.code import MOpcode
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
from pymonkey.object.object import CompliedFunction
from pymonkey.util import flog
from pymonkey.vm.frame import Frame


@dataclass
class VM:
    constants: List[MObject]
    stack: List[MObject]
    stack_pointer: int
    last_pop: MObject
    globals: dict[int, MObject]
    frames: list[Frame]
    frames_index: int

    def __init__(self, bytecode: Bytecode) -> None:
        self.constants = bytecode.constants
        self.stack = []
        self.stack_pointer = 0
        self.last_pop = MNullObject()
        self.globals = {}
        main_fn = CompliedFunction(bytecode.instructions, -1, 0)
        main_frame = Frame(main_fn, -1, 0)
        self.frames = [main_frame]
        self.frames_index = 1

    @classmethod
    def from_bytecode_pickle(cls, file_name: str) -> Self:
        with open(file_name, "br") as file:
            bytecode = pickle.load(file)

        return VM(bytecode)

    def __str__(self) -> str:
        return f"VM(sp={self.stack_pointer}, stack={self.stack})"

    def stack_top(self) -> None | MObject:
        if self.stack_pointer == 0:
            return None
        return self.stack[self.stack_pointer - 1]

    @flog
    def stack_push(self, obj: MObject) -> None:
        self.stack.append(obj)
        self.stack_pointer += 1

    @flog
    def stack_pop(self) -> MObject:
        self.stack_pointer -= 1
        self.last_pop = self.stack.pop()
        return self.last_pop

    def current_frame(self) -> Frame:
        return self.frames[self.frames_index - 1]

    @flog
    def push_frame(self, frame: Frame) -> None:
        self.frames.append(frame)
        self.frames_index += 1

    @flog
    def pop_frame(self) -> Frame:
        self.frames_index -= 1
        return self.frames.pop(self.frames_index)

    @flog
    def run(self) -> None:
        ip = 0
        opargs = 0
        op = MOpcode.OpUndefined

        while self.current_frame().ip < len(self.current_frame().instructions) - 1:
            self.current_frame().ip += 1

            ip = self.current_frame().ip
            op = self.current_frame().instructions.get_opcode(ip)
            opargs = self.current_frame().instructions.get_opargs(ip)

            if op == MOpcode.OpConstant:
                self.stack_push(self.constants[opargs])

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
                self.current_frame().ip = opargs - 1

            elif op == MOpcode.OpJumpNotTruthy:
                condition = self.stack_pop()
                if isinstance(condition, MBooleanObject) and not condition.value:
                    self.current_frame().ip = opargs - 1

            elif op == MOpcode.OpNull:
                self.stack_push(MNullObject())

            elif op == MOpcode.OpSetGlobal:
                self.globals[opargs] = self.stack_pop()

            elif op == MOpcode.OpGetGlobal:
                self.stack_push(self.globals[opargs])

            elif op == MOpcode.OpArray:
                arr = self.build_array(self.stack_pointer - opargs, self.stack_pointer)
                self.stack_pointer -= opargs
                self.stack_push(arr)

            elif op == MOpcode.OpHash:
                hashmap = self.build_hashmap(
                    self.stack_pointer - opargs, self.stack_pointer
                )
                self.stack_pointer -= opargs
                self.stack_push(hashmap)

            elif op == MOpcode.OpIndex:
                index = self.stack_pop()
                left = self.stack_pop()
                self.execute_index_expression(left, index)

            elif op == MOpcode.OpCall:
                fn = self.stack[self.stack_pointer - 1 - opargs]
                if not isinstance(fn, CompliedFunction):
                    raise ValueError("not a function")
                if opargs != fn.num_parameters:
                    raise ValueError("wrong number of arguments")
                frame = Frame(fn, -1, self.stack_pointer - opargs)
                self.push_frame(frame)
                self.stack_pointer += fn.num_locals

            elif op == MOpcode.OpReturnValue:
                return_value = self.stack_pop()
                self.pop_frame()
                self.stack_pop()
                self.stack_push(return_value)

            elif op == MOpcode.OpReturn:
                self.pop_frame()
                self.stack_pop()
                self.stack_push(MNullObject())

            elif op == MOpcode.OpSetLocal:
                poped_obj = self.stack_pop()
                for _ in range(
                    self.current_frame().base_pointer + opargs - len(self.stack) + 1
                ):
                    self.stack_push(MNullObject())
                self.stack[self.current_frame().base_pointer + opargs] = poped_obj

            elif op == MOpcode.OpGetLocal:
                self.stack_push(self.stack[self.current_frame().base_pointer + opargs])

            elif op == MOpcode.OpReturnValue:
                return_value = self.stack_pop()
                frame = self.pop_frame()
                self.stack_pointer = frame.base_pointer - 1
                self.stack_push(return_value)

            elif op == MOpcode.OpReturn:
                frame = self.pop_frame()
                self.stack_pointer = frame.base_pointer - 1
                self.stack_push(MNullObject())

            else:
                raise TypeError("unknown op code")

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
