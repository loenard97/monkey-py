from dataclasses import dataclass

from pymonkey.code.code import Instructions
from pymonkey.object.object import CompliedFunction


@dataclass
class Frame:
    function: CompliedFunction
    ip: int

    @property
    def instructions(self) -> Instructions:
        return self.function.instructions
