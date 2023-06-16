from .token import *

class Lexer:

    def __init__(self, input):
        self._input = input
        self._position = 0
        self._read_position = 0
        self._ch = ''
        self._read_ch()

    def __iter__(self):
        return self

    def __next__(self) -> Token:
        while self._ch.isspace():
            self._read_ch()

        token = Token(ILLEGAL, ILLEGAL)
        match self._ch:
            case "=":
                if self._next_ch() == "=":
                    self._read_ch()
                    token = Token(EQUAL, EQUAL)
                else:
                    token = Token(ASSIGN, ASSIGN)
            case "+":
                token = Token(PLUS, PLUS)
            case "-":
                token = Token(MINUS, MINUS)
            case "!":
                if self._next_ch() == "=":
                    self._read_ch()
                    token = Token(NOTEQUAL, NOTEQUAL)
                else:
                    token = Token(BANG, BANG)
            case "*":
                token = Token(ASTERISK, ASTERISK)
            case "/":
                token = Token(SLASH, SLASH)
            case "<":
                token = Token(LESSER, LESSER)
            case ">":
                token = Token(GREATER, GREATER)

            case ",":
                token = Token(COMMA, COMMA)
            case ";":
                token = Token(SEMICOLON, SEMICOLON)
            case "(":
                token = Token(LPAREN, LPAREN)
            case ")":
                token = Token(RPAREN, RPAREN)
            case "{":
                token = Token(LBRACE, LBRACE)
            case "}":
                token = Token(RBRACE, RBRACE)

            case "\0":
                raise StopIteration

            case _:
                if self._ch.isalpha():
                    pos = self._position
                    while self._ch.isalpha():
                        self._read_ch()
                    identifier = self._input[pos:self._position]
                    if identifier in keywords:
                        return Token(KEYWORD, identifier)
                    else:
                        return Token(IDENTIFIER, identifier)

                elif self._ch.isnumeric():
                    pos = self._position
                    while self._ch.isnumeric():
                        self._read_ch()
                    number = self._input[pos:self._position]
                    return Token(NUMBER, number)
                
                else:
                    token = Token(ILLEGAL, ILLEGAL)

        self._read_ch()
        return token

    def _read_ch(self):
        try:
            self._ch = self._input[self._read_position]
        except IndexError:
            self._ch = '\0'
        else:
            self._position = self._read_position
            self._read_position += 1

    def _next_ch(self) -> str:
        try:
            return self._input[self._read_position]
        except IndexError:
            return '\0'

