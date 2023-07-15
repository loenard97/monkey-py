from dataclasses import dataclass

from pymonkey.code.code import Instructions


@dataclass
class CompliedFunction:
    instructions: Instructions
