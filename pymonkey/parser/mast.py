from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Hashable, List

from pymonkey.lexer.mtoken import MToken


class MNode(ABC):
    token: MToken = NotImplemented

    @abstractmethod
    def __str__(self):
        raise NotImplementedError


class MStatement(MNode):
    pass


class MExpression(MNode):
    pass


class MValuedExpression(MExpression):
    """
    Valued Expression that can be hashed and therefore used as dict keys.
    Child classes need to use @dataclass(eq=False, frozen=True), otherwise dataclass overwrites __hash__ to None.
    See unsafe_hash parameter of dataclass:
    https://docs.python.org/3/library/dataclasses.html
    """

    value: Hashable = NotImplemented

    def __hash__(self) -> int:
        # hash only self.value and not self.token, to ensure same hashes between equal valued MExpressions.
        # include type(self) in hash, to ensure different hashes between different types.
        return (type(self), self.value).__hash__()


@dataclass
class MProgram(MNode):
    statements: List[MStatement]
    token = MToken()

    def __str__(self):
        return "\n".join(str(s) for s in self.statements)


@dataclass
class MIdentifier(MExpression):
    value: str
    token: MToken

    def __str__(self):
        return f"{self.value}"


@dataclass
class MLetStatement(MStatement):
    name: MIdentifier
    value: MExpression
    token: MToken

    def __str__(self):
        return f"let {self.name} = {self.value};"


@dataclass
class MReturnStatement(MStatement):
    value: MExpression
    token: MToken

    def __str__(self):
        return f"return {self.value};"


@dataclass
class MExpressionStatement(MStatement):
    expression: MExpression
    token: MToken

    def __str__(self):
        return self.expression.__str__() + ";"


@dataclass
class MBlockStatement(MStatement):
    statements: List[MStatement]
    token: MToken

    def __str__(self):
        return "\n".join(str(s) for s in self.statements)


@dataclass(eq=False, frozen=True)
class MBooleanExpression(MValuedExpression):
    value: bool
    token: MToken

    def __str__(self):
        return f"{self.value}".lower()


@dataclass(eq=False, frozen=True)
class MIntegerExpression(MValuedExpression):
    value: int
    token: MToken

    def __str__(self):
        return f"{self.value}"


@dataclass(eq=False, frozen=True)
class MStringExpression(MValuedExpression):
    value: str
    token: MToken

    def __str__(self):
        return f'"{self.value}"'


@dataclass
class MArrayExpression(MExpression):
    value: List[MExpression]
    token: MToken

    def __str__(self):
        args = ", ".join([str(e) for e in self.value])
        return f"[{args}]"


@dataclass
class MPrefixExpression(MExpression):
    operator: str
    right: MExpression
    token: MToken

    def __str__(self):
        return f"{self.operator}{self.right}"


@dataclass
class MInfixExpression(MExpression):
    operator: str
    left: MExpression
    right: MExpression
    token: MToken

    def __str__(self):
        return f"{self.left} {self.operator} {self.right}"


@dataclass
class MIfExpression(MExpression):
    condition: MExpression
    consequence: MBlockStatement
    alternative: MBlockStatement | None
    token: MToken

    def __str__(self):
        if self.alternative is None:
            return f"if ({self.condition}) {{ {self.consequence} }}"
        return (
            f"if ({self.condition}) {{ {self.consequence} }} else {{"
            f" {self.alternative} }}"
        )


@dataclass
class MFunctionExpression(MExpression):
    parameters: List[MExpression]
    body: MBlockStatement
    token: MToken

    def __str__(self):
        params = ", ".join([str(p) for p in self.parameters])
        return f"{self.token.literal}({params}) {{ {self.body} }}"


@dataclass
class MCallExpression(MExpression):
    function: MExpression
    arguments: List[MExpression]
    token: MToken

    def __str__(self):
        args = ", ".join([str(a) for a in self.arguments])
        return f"{self.function}({args})"


@dataclass
class MIndexExpression(MExpression):
    left: MExpression
    index: MExpression
    token: MToken

    def __str__(self):
        return f"{self.left}[{self.index}]"


@dataclass
class MHashMapExpression(MExpression):
    pairs: Dict[MValuedExpression, MExpression]
    token: MToken

    def __str__(self):
        pairs = ", ".join([f"{key}: {value}" for key, value in self.pairs.items()])
        return f"{{{pairs}}}"
