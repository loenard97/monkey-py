from dataclasses import dataclass

from pymonkey.code.code import Instructions


@dataclass
class CompliedFunction:
    instructions: Instructions
    num_locals: int
    num_parameters: int
