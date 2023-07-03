from dataclasses import dataclass
from typing import List

from pymonkey.code.code import Encoder, Instructions, MOpcode
from pymonkey.evaluator.mobject import MIntegerObject, MObject
from pymonkey.parser.mast import (
    MBooleanExpression,
    MExpressionStatement,
    MInfixExpression,
    MIntegerExpression,
    MNode,
    MProgram,
)


@dataclass
class Compiler:
    instructions: Instructions
    constants: List[MObject]

    def __init__(self) -> None:
        self.instructions = Instructions([])
        self.constants = []

    def compile(self, node: MNode) -> None:
        if isinstance(node, MProgram):
            for stmt in node.statements:
                self.compile(stmt)

        elif isinstance(node, MExpressionStatement):
            self.compile(node.expression)
            self.emit(MOpcode.OpPop)

        elif isinstance(node, MInfixExpression):
            self.compile(node.left)
            self.compile(node.right)

            if node.operator == "+":
                self.emit(MOpcode.OpAdd)

            elif node.operator == "-":
                self.emit(MOpcode.OpSub)

            elif node.operator == "*":
                self.emit(MOpcode.OpMul)

            elif node.operator == "/":
                self.emit(MOpcode.OpDiv)

            else:
                raise TypeError("unknown operator")

        elif isinstance(node, MIntegerExpression):
            integer = MIntegerObject(node.value)
            self.emit(MOpcode.OpConstant, self.add_constant(integer))

        elif isinstance(node, MBooleanExpression):
            if node.value:
                self.emit(MOpcode.OpTrue)
            else:
                self.emit(MOpcode.OpFalse)

        else:
            raise TypeError(f"unknown MObject {node}")

    def emit(self, op: MOpcode, *operands: int) -> int:
        ins = Encoder.make(op, *operands)
        return self.add_instruction(ins)

    def add_instruction(self, ins: bytearray) -> int:
        pos_new_ins = len(self.instructions.instructions)
        self.instructions.append(ins)
        return pos_new_ins

    def add_constant(self, obj: MObject) -> int:
        self.constants.append(obj)
        return len(self.constants) - 1

    def bytecode(self) -> "Bytecode":
        return Bytecode(self.instructions, self.constants)


@dataclass
class Bytecode:
    instructions: Instructions
    constants: List[MObject]


class Decompiler:
    @classmethod
    def read_operands(cls) -> None:
        pass
        # for i, width in enumerate(def.operand_widths):
        #     if width == 2:
        #         pass
