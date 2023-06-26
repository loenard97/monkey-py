from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


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


KEYWORDS = ["fn", "let", "true", "false", "if", "else", "return"]


@dataclass
class TokenPosition:
    file: str
    line: int
    pos: int


@dataclass
class MToken:
    type: TokenType = TokenType.Illegal
    literal: Optional[str] = None
    position: TokenPosition = TokenPosition("", 0, 0)

    def __str__(self):
        return f"Token <{self.type}, {self.literal}, {self.position.file}, {self.position.line}, {self.position.pos}>"

    def __eq__(self, other: "MToken | str") -> bool:
        if isinstance(other, MToken):
            return self.type == other.type and self.literal == other.literal

        if isinstance(other, str):
            return self.type == other or self.literal == other

        raise TypeError("can only compare MToken to MToken or str")
