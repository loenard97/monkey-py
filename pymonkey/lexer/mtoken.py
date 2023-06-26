from dataclasses import dataclass
from enum import Enum, auto

class TokenType(Enum):
    Identifier = auto()
    Number = auto()
    String = auto()
    Keyword = auto()
    Eof = auto()
    Illegal = auto()

    Assign = auto()
    Plus = auto()
    Minus = auto()
    Bang = auto()
    Asterisk = auto()
    Slash = auto()
    Lesser = auto()
    LesserEqual = auto()
    Greater = auto()
    GreaterEqual = auto()
    Equal = auto()
    NotEqual = auto()

    Comma = auto()
    Semicolon = auto()
    Colon = auto()
    LParen = auto()
    RParen = auto()
    LBrace = auto()
    RBrace = auto()
    LBracket = auto()
    RBracket = auto()


IDENTIFIER = "Identifier"
NUMBER = "Number"
STRING = "String"
KEYWORD = "Keyword"
EOF = "Eof"
ILLEGAL = "Illegal"

FUNCTION = "function"
LET = "let"
TRUE = "true"
FALSE = "false"
IF = "if"
ELSE = "else"
RETURN = "return"

ASSIGN = "="
PLUS = "+"
MINUS = "-"
BANG = "!"
ASTERISK = "*"
SLASH = "/"
LESSER = "<"
GREATER = ">"

COMMA = ","
SEMICOLON = ";"
COLON = ":"
LPAREN = "("
RPAREN = ")"
LBRACE = "{"
RBRACE = "}"
LBRACKET = "["
RBRACKET = "]"
EQUAL = "=="
NOTEQUAL = "!="

keywords = {
    "fn": FUNCTION,
    "let": LET,
    "true": TRUE,
    "false": FALSE,
    "if": IF,
    "else": ELSE,
    "return": RETURN,
}


@dataclass
class MToken:
    type: TokenType
    literal: str
    file: str
    line: int
    pos: int

    def __init__(self, type, literal, file="", line=0, pos=0):
        self.type = type
        self.literal = literal
        self.file = file
        self.line = line
        self.pos = pos

    @classmethod
    def from_empty(cls):
        return MToken(ILLEGAL, ILLEGAL, "", 0, 0)

    def __str__(self):
        return (
            f"Token <{self.type}, {self.literal}, {self.file}, {self.line},"
            f" {self.pos}>"
        )

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, MToken):
            print("eq")
            print(f"{self.type=} {__value.type=} {self.literal=} {__value.type=}")
            return self.type == __value.type and self.literal == __value.literal

        if isinstance(__value, str):
            return self.type == __value or self.literal == __value

        return False
