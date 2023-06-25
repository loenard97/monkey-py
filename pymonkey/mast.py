from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from pymonkey.mtoken import ILLEGAL, MToken


class MNode(ABC):
    token: MToken = NotImplemented

    @abstractmethod
    def __str__(self):
        raise NotImplementedError


class MStatement(MNode):
    pass


class MExpression(MNode):
    pass


@dataclass
class MProgram(MNode):
    statements: List[MStatement]
    token = MToken(ILLEGAL, ILLEGAL, "", 0, 0)

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


@dataclass
class MBooleanExpression(MExpression):
    value: bool
    token: MToken

    def __str__(self):
        return f"{self.value}".lower()


@dataclass
class MIntegerExpression(MExpression):
    value: int
    token: MToken

    def __str__(self):
        return f"{self.value}"


@dataclass
class MStringExpression(MExpression):
    value: str
    token: MToken

    def __str__(self):
        return f'"{self.value}"'


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
