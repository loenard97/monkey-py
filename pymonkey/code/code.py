from dataclasses import dataclass
from enum import Enum
from typing import List


@dataclass
class Instructions:
    instructions: List[bytearray]

    def __len__(self) -> int:
        return self.instructions.__len__()

    def __str__(self) -> str:
        offset = 0
        ret = []
        for instruction in self.instructions:
            operation = MOpcode(instruction[0])
            operands_str = ", ".join([f"0x{b:02x}" for b in instruction[1:]])
            ret.append(f"{offset:04d} {operation} {operands_str}")
            offset += len(instruction)
        return "\n".join(ret)

    def append(self, ins: bytearray):
        self.instructions.append(ins)


class MOpcode(Enum):
    OpConstant = 0x01


definitions = {
    "OpConstant": [0, 0],
}


@dataclass
class MDefinition:
    name: str
    operand_widths: List[int]

    @classmethod
    def lookup(cls, op: MOpcode) -> "None | MDefinition":
        if op == MOpcode.OpConstant:
            return MDefinition("OpConstant", [2])

        return None


class Encoder:
    @classmethod
    def make(cls, op: MOpcode, *operands) -> bytearray:
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
