from typing import List
from abc import ABC
from dataclasses import dataclass

from .token import *


class Node(ABC):
    pass


class Statement(Node):
    pass


@dataclass
class EmptyStatement(Statement):
    pass


class Expression(Node):
    pass


@dataclass
class EmptyExpression(Expression):
    pass


@dataclass
class Program:
    
    statements: List[Statement]


@dataclass
class Identifier(Expression):

    token: Token
    value: str


@dataclass
class LetStatement(Statement):
    
    token: Token
    name: Identifier
    value: Expression


@dataclass
class ReturnStatement(Statement):

    token: Token
    value: Expression


@dataclass
class ExpressionStatement(Statement):

    token: Token
    expression: Expression


@dataclass
class BlockStatement(Statement):

    token: Token
    statements: List[Statement]


# ----- Expressions ----- #

@dataclass
class Boolean(Expression):

    token: Token
    value: bool


@dataclass
class Integer(Expression):

    token: Token
    value: int


@dataclass
class Prefix(Expression):

    token: Token
    operator: str
    right: Expression


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
    alternative: BlockStatement | EmptyStatement


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

