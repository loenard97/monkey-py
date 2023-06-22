from dataclasses import dataclass

TokenType = str

IDENTIFIER = "Identifier"
NUMBER = "Number"
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
LPAREN = "("
RPAREN = ")"
LBRACE = "{"
RBRACE = "}"
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

    def __str__(self):
        return (
            f"Token <{self.type}, {self.literal}, {self.file}, {self.line},"
            f" {self.pos}>"
        )

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, MToken):
            print("eq")
            print(
                f"{self.type=} {__value.type=} {self.literal=} {__value.type=}"
            )
            return (
                self.type == __value.type and self.literal == __value.literal
            )

        if isinstance(__value, str):
            return self.type == __value or self.literal == __value

        return False
