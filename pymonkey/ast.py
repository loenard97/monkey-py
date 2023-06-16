from typing import List
from abc import ABC
from dataclasses import dataclass

from .token import *


class Node(ABC):
    pass


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

    token: Token
    value: str

    def __str__(self):
        return f"{self.value}"


@dataclass
class LetStatement(Statement):
    
    token: Token
    name: Identifier
    value: Expression
    
    def __str__(self):
        return f"let {self.name} = {self.value}"


@dataclass
class ReturnStatement(Statement):

    token: Token
    value: Expression

    def __str__(self):
        return f"return {self.value}"


@dataclass
class ExpressionStatement(Statement):

    token: Token
    expression: Expression

    def __str__(self):
        return self.expression.__str__()


@dataclass
class BlockStatement(Statement):

    token: Token
    statements: List[Statement]

    def __str__(self):
        return '\n'.join(str(s) for s in self.statements)


# ----- Expressions ----- #

@dataclass
class Boolean(Expression):

    token: Token
    value: bool

    def __str__(self):
        return f"{self.value}"


@dataclass
class Integer(Expression):

    token: Token
    value: int

    def __str__(self):
        return f"{self.value}"


@dataclass
class Prefix(Expression):

    token: Token
    operator: str
    right: Expression

    def __str__(self):
        return f"{self.operator}{self.right}"


@dataclass
class Infix(Expression):

    token: Token
    operator: str
    left: Expression
    right: Expression


@dataclass
class If(Expression):

    token: Token
    condition: Expression
    consequence: BlockStatement
    alternative: BlockStatement | None


@dataclass
class Function(Expression):

    token: Token
    parameters: List[Expression]
    body: BlockStatement


@dataclass
class Call(Expression):

    token: Token
    function: Expression
    arguments: List[Expression]

