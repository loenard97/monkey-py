from typing import List
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .token import *


class Node(ABC):

    token: Token = NotImplemented 

    @abstractmethod
    def __str__(self):
        raise NotImplementedError


class Statement(Node):

    pass


class Expression(Node):

    pass


@dataclass
class Program:
    
    statements: List[Statement]

    def __str__(self):
        return '\n'.join(str(s) for s in self.statements)


@dataclass
class Identifier(Expression):

    value: str
    token: Token

    def __str__(self):
        return f"{self.value}"


@dataclass
class LetStatement(Statement):
    
    name: Identifier
    value: Expression
    token: Token
    
    def __str__(self):
        return f"let {self.name} = {self.value};"


@dataclass
class ReturnStatement(Statement):

    value: Expression
    token: Token

    def __str__(self):
        return f"return {self.value};"


@dataclass
class ExpressionStatement(Statement):

    expression: Expression
    token: Token

    def __str__(self):
        return self.expression.__str__() + ";"


@dataclass
class BlockStatement(Statement):

    statements: List[Statement]
    token: Token

    def __str__(self):
        return '\n'.join(str(s) for s in self.statements)


# ----- Expressions ----- #

@dataclass
class BooleanExpression(Expression):

    value: bool
    token: Token

    def __str__(self):
        return f"{self.value}".lower()


@dataclass
class IntegerExpression(Expression):

    value: int
    token: Token

    def __str__(self):
        return f"{self.value}"


@dataclass
class PrefixExpression(Expression):

    operator: str
    right: Expression
    token: Token

    def __str__(self):
        return f"{self.operator}{self.right}"


@dataclass
class InfixExpression(Expression):

    operator: str
    left: Expression
    right: Expression
    token: Token

    def __str__(self):
        return f"{self.left} {self.operator} {self.right}"


@dataclass
class IfExpression(Expression):

    condition: Expression
    consequence: BlockStatement
    alternative: BlockStatement | None
    token: Token

    def __str__(self):
        if self.alternative is None:
            return f"if ({self.condition}) {{ {self.consequence} }}"
        return f"if ({self.condition}) {{ {self.consequence} }} else {{ {self.alternative} }}"


@dataclass
class FunctionExpression(Expression):

    parameters: List[Expression]
    body: BlockStatement
    token: Token

    def __str__(self):
        params = ', '.join([str(p) for p in self.parameters])
        return f"{self.token.literal}({params}) {{ {self.body} }}"


@dataclass
class CallExpression(Expression):

    function: Expression
    arguments: List[Expression]
    token: Token

    def __str__(self):
        args = ', '.join([str(a) for a in self.arguments])
        return f"{self.function}({args})"

