from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

KEYWORDS = ["fn", "let", "true", "false", "if", "else", "return"]


class MTokenType(Enum):
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


@dataclass
class MTokenPosition:
    file: str
    line: int
    pos: int


@dataclass
class MToken:
    type: MTokenType = MTokenType.Illegal
    literal: str = ""
    position: Optional[MTokenPosition] = None
