from dataclasses import dataclass
from typing import List

from pymonkey.code.code import Encoder, Instructions, MOpcode
from pymonkey.evaluator.mobject import MIntegerObject, MObject
from pymonkey.parser.mast import (
    MBlockStatement,
    MBooleanExpression,
    MExpressionStatement,
    MIfExpression,
    MInfixExpression,
    MIntegerExpression,
    MNode,
    MPrefixExpression,
    MProgram,
)
from pymonkey.util import flog


@dataclass
class EmittedInstruction:
    opcode: MOpcode
    position: int


@dataclass
class Compiler:
    instructions: Instructions
    constants: List[MObject]
    last_instruction: EmittedInstruction
    previous_instruction: EmittedInstruction

    def __init__(self) -> None:
        self.instructions = Instructions([])
        self.constants = []
        self.last_instruction = EmittedInstruction(MOpcode.OpUndefined, 0)
        self.previous_instruction = EmittedInstruction(MOpcode.OpUndefined, 0)

    def __str__(self) -> str:
        return f"Compiler(instructions: {self.instructions.instructions}, constants: {self.constants})"

    @flog
    def compile(self, node: MNode) -> None:
        if isinstance(node, MProgram):
            for stmt in node.statements:
                self.compile(stmt)

        elif isinstance(node, MExpressionStatement):
            self.compile(node.expression)
            self.emit(MOpcode.OpPop)

        elif isinstance(node, MInfixExpression):
            if node.operator == "<":
                self.compile(node.right)
                self.compile(node.left)
                self.emit(MOpcode.OpGreater)
                return

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

            elif node.operator == ">":
                self.emit(MOpcode.OpGreater)

            elif node.operator == "==":
                self.emit(MOpcode.OpEqual)

            elif node.operator == "!=":
                self.emit(MOpcode.OpNotEqual)

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

        elif isinstance(node, MPrefixExpression):
            self.compile(node.right)

            if node.operator == "-":
                self.emit(MOpcode.OpMinus)

            elif node.operator == "!":
                self.emit(MOpcode.OpBang)

            else:
                raise ValueError

        elif isinstance(node, MIfExpression):
            print("compile if")
            print("condition")
            self.compile(node.condition)
            print("jump not true")
            jump_not_truthy_pos = self.emit(MOpcode.OpJumpNotTruthy, 65535)
            print("consequence")
            self.compile(node.consequence)
            if self.last_instruction.opcode == MOpcode.OpPop:
                self.instructions.pop()
                self.last_instruction = self.previous_instruction

            after_consequence_pos = len(self.instructions)

            print("jump not truthy", self.instructions[jump_not_truthy_pos])

            self.instructions.instructions[jump_not_truthy_pos] = Encoder.make(MOpcode.OpJumpNotTruthy, after_consequence_pos)

            print("jump not true changed to", self.instructions[jump_not_truthy_pos])

        elif isinstance(node, MBlockStatement):
            for stmt in node.statements:
                self.compile(stmt)

        else:
            raise TypeError(f"unknown MObject {node}")

    @flog
    def emit(self, op: MOpcode, *operands: int) -> int:
        ins = Encoder.make(op, *operands)
        pos = self.add_instruction(ins)
        self.previous_instruction = self.last_instruction
        self.last_instruction = EmittedInstruction(op, pos)
        return pos

    @flog
    def add_instruction(self, ins: bytearray) -> int:
        pos_new_ins = len(self.instructions.instructions)
        self.instructions.append(ins)
        return pos_new_ins

    @flog
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
