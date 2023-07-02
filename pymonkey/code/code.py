from dataclasses import dataclass
from enum import Enum
from typing import Generator, List


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
            operands_str = " ".join([f"0x{b:02x}" for b in instruction[1:]])
            ret.append(f"{offset:04d} {operation}{' ' if operands_str else ''}{operands_str}")
            offset += len(instruction)
        return "\n".join(ret)

    def __getitem__(self, index: int | slice) -> bytearray | List[bytearray]:
        return self.instructions.__getitem__(index)

    def __iter__(self) -> Generator[bytearray, None, None]:
        return (ins for ins in self.instructions)

    def append(self, ins: bytearray):
        self.instructions.append(ins)


class MOpcode(Enum):
    OpConstant = 0x01
    OpAdd = 0x02


definitions = {
    "OpConstant": [2],
    "OpAdd": [],
}


@dataclass
class MDefinition:
    name: str
    operand_widths: List[int]

    @classmethod
    def lookup(cls, op: MOpcode) -> "None | MDefinition":
        try:
            return MDefinition(op.name, definitions[op.name])
        except KeyError:
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
