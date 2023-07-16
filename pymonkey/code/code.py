from dataclasses import dataclass
from enum import Enum
from typing import Generator


@dataclass
class Instructions:
    instructions: list[bytearray]

    def __len__(self) -> int:
        return self.instructions.__len__()

    def __str__(self) -> str:
        offset = 0
        ret = []
        for instruction in self.instructions:
            operation = MOpcode(instruction[0])
            operands_str = " ".join([f"0x{b:02x}" for b in instruction[1:]])
            ret.append(
                f"{offset:04d} {operation}{' ' if operands_str else ''}{operands_str}"
            )
            offset += len(instruction)
        return "\n".join(ret)

    def __getitem__(self, index: int | slice) -> bytearray | list[bytearray]:
        return self.instructions.__getitem__(index)

    def __iter__(self) -> Generator[bytearray, None, None]:
        return (ins for ins in self.instructions)

    def get_opcode(self, index: int) -> "MOpcode":
        return MOpcode(self.instructions[index][0])

    def get_opargs(self, index: int) -> int:
        return int.from_bytes(
            self.instructions[index][1:], byteorder="big", signed=False
        )

    def append(self, ins: bytearray) -> None:
        self.instructions.append(ins)

    def pop(self) -> bytearray:
        return self.instructions.pop()


class MOpcode(Enum):
    OpConstant = 0x01
    OpPop = 0x02

    OpAdd = 0x03
    OpSub = 0x04
    OpMul = 0x05
    OpDiv = 0x06

    OpTrue = 0x07
    OpFalse = 0x08

    OpEqual = 0x09
    OpNotEqual = 0x0A
    OpGreater = 0x0B

    OpMinus = 0x0C
    OpBang = 0x0D

    OpJumpNotTruthy = 0x0E
    OpJump = 0x0F

    OpNull = 0x10

    OpGetGlobal = 0x11
    OpSetGlobal = 0x12

    OpArray = 0x13
    OpHash = 0x14
    OpIndex = 0x15

    OpCall = 0x16
    OpReturnValue = 0x17
    OpReturn = 0x18

    OpGetLocal = 0x19
    OpSetLocal = 0x20

    OpUndefined = 0xFF

    @property
    def arg_length(self) -> int:
        if (
            self == MOpcode.OpConstant
            or self == MOpcode.OpJumpNotTruthy
            or self == MOpcode.OpJump
            or self == MOpcode.OpGetGlobal
            or self == MOpcode.OpSetGlobal
            or self == MOpcode.OpArray
            or self == MOpcode.OpHash
        ):
            return 2
        return 0

    def make_bytearray(self, *args: int) -> bytearray:
        instruction = bytearray()
        instruction.append(self.value)

        for arg in args:
            instruction += arg.to_bytes(
                length=self.arg_length, byteorder="big", signed=False
            )

        return instruction


definitions: dict[str, list[int]] = {
    "OpConstant": [2],
    "OpPop": [],
    "OpAdd": [],
    "OpSub": [],
    "OpMul": [],
    "OpDiv": [],
    "OpTrue": [],
    "OpFalse": [],
    "OpEqual": [],
    "OpNotEqual": [],
    "OpGreater": [],
    "OpMinus": [],
    "OpBang": [],
    "OpJumpNotTruthy": [2],
    "OpJump": [2],
    "OpNull": [],
    "OpGetGlobal": [2],
    "OpSetGlobal": [2],
    "OpArray": [2],
    "OpHash": [2],
    "OpIndex": [],
    "OpCall": [2],
    "OpReturnValue": [],
    "OpReturn": [],
    "OpUndefined": [],
    "OpGetLocal": [2],
    "OpSetLocal": [2],
}


@dataclass
class MDefinition:
    name: str
    operand_widths: list[int]

    @classmethod
    def lookup(cls, op: MOpcode) -> "None | MDefinition":
        try:
            return MDefinition(op.name, definitions[op.name])
        except KeyError:
            return None


class Encoder:
    @classmethod
    def make(cls, op: MOpcode, *operands: int) -> bytearray:
        definition = MDefinition.lookup(op)
        if definition is None:
            return bytearray()

        instruction = bytearray()
        instruction.append(op.value)

        for i, operand in enumerate(operands):
            width = definition.operand_widths[i]

            if width == 2:
                instruction += operand.to_bytes(2, "big")

        return instruction
