from dataclasses import dataclass


TokenType = str

IDENTIFIER  = "Identifier"
NUMBER      = "Number"
KEYWORD     = "Keyword"
EOF         = "Eof"
ILLEGAL     = "Illegal"

FUNCTION    = "function"
LET         = "let"
TRUE        = "true"
FALSE       = "false"
IF          = "if"
ELSE        = "else"
RETURN      = "return"

ASSIGN      = "="
PLUS        = "+"
MINUS       = "-"
BANG        = "!"
ASTERISK    = "*"
SLASH       = "/"
LESSER      = "<"
GREATER     = ">"

COMMA       = ","
SEMICOLON   = ";"
LPAREN      = "("
RPAREN      = ")"
LBRACE      = "{"
RBRACE      = "}"
EQUAL       = "=="
NOTEQUAL    = "!="

keywords = {
    "fn"    : FUNCTION,
    "let"   : LET,
    "true"  : TRUE,
    "false" : FALSE,
    "if"    : IF,
    "else"  : ELSE,
    "return": RETURN,
}


@dataclass
class Token:

    type: TokenType
    literal: str

    def __init__(self, type, literal):
        self.type = type
        self.literal = literal


    def __str__(self):
        return f"{self.type}.{self.literal}"


    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Token):
            return self.type == __value.type and self.literal == __value.type
        
        if isinstance(__value, str):
            return self.type == __value or self.literal == __value

        return False

