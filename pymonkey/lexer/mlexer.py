from dataclasses import dataclass
from typing import List

from pymonkey.lexer.mtoken import (
    ASSIGN,
    ASTERISK,
    BANG,
    COLON,
    COMMA,
    EQUAL,
    GREATER,
    IDENTIFIER,
    ILLEGAL,
    KEYWORD,
    LBRACE,
    LBRACKET,
    LESSER,
    LPAREN,
    MINUS,
    NOTEQUAL,
    NUMBER,
    PLUS,
    RBRACE,
    RBRACKET,
    RPAREN,
    SEMICOLON,
    SLASH,
    STRING,
    MToken,
    keywords,
)


@dataclass
class MLexerError:
    token: MToken
    msg: str


class MLexer:
    def __init__(self, input):
        self._input = input
        self._position = 0
        self._read_position = 0
        self._ch = ""
        self.cur_file = ""
        self.cur_line = 0
        self.cur_pos = 0
        self._read_ch()

        self.errors: List[MLexerError] = []

        self._n_braces = 0
        self._n_paren = 0
        self._n_brackets = 0
        self._last_brace = MToken.from_empty()
        self._last_paren = MToken.from_empty()
        self._last_bracket = MToken.from_empty()

    def __iter__(self):
        return self

    def __next__(self) -> MToken:
        while self._ch.isspace():
            if self._ch == "\n":
                self.cur_line += 1
                self.cur_pos = 0
            self._read_ch()

        token = MToken(ILLEGAL, ILLEGAL, self.cur_file, self.cur_line, self.cur_pos)
        match self._ch:
            case "=":
                if self._next_ch() == "=":
                    self._read_ch()
                    token = MToken(
                        EQUAL,
                        EQUAL,
                        self.cur_file,
                        self.cur_line,
                        self.cur_pos,
                    )
                else:
                    token = MToken(
                        ASSIGN,
                        ASSIGN,
                        self.cur_file,
                        self.cur_line,
                        self.cur_pos,
                    )
            case "+":
                token = MToken(PLUS, PLUS, self.cur_file, self.cur_line, self.cur_pos)
            case "-":
                token = MToken(MINUS, MINUS, self.cur_file, self.cur_line, self.cur_pos)
            case "!":
                if self._next_ch() == "=":
                    self._read_ch()
                    token = MToken(
                        NOTEQUAL,
                        NOTEQUAL,
                        self.cur_file,
                        self.cur_line,
                        self.cur_pos,
                    )
                else:
                    token = MToken(
                        BANG, BANG, self.cur_file, self.cur_line, self.cur_pos
                    )
            case "*":
                token = MToken(
                    ASTERISK,
                    ASTERISK,
                    self.cur_file,
                    self.cur_line,
                    self.cur_pos,
                )
            case "/":
                token = MToken(SLASH, SLASH, self.cur_file, self.cur_line, self.cur_pos)
            case "<":
                token = MToken(
                    LESSER, LESSER, self.cur_file, self.cur_line, self.cur_pos
                )
            case ">":
                token = MToken(
                    GREATER,
                    GREATER,
                    self.cur_file,
                    self.cur_line,
                    self.cur_pos,
                )

            case ",":
                token = MToken(COMMA, COMMA, self.cur_file, self.cur_line, self.cur_pos)
            case ";":
                token = MToken(
                    SEMICOLON,
                    SEMICOLON,
                    self.cur_file,
                    self.cur_line,
                    self.cur_pos,
                )
            case ":":
                token = MToken(COLON, COLON, self.cur_file, self.cur_line, self.cur_pos)
            case '"':
                token = MToken(
                    STRING,
                    self._read_string(),
                    self.cur_file,
                    self.cur_line,
                    self.cur_pos,
                )
            case "(":
                token = MToken(
                    LPAREN, LPAREN, self.cur_file, self.cur_line, self.cur_pos
                )
                self._n_paren += 1
                self._last_paren = token
            case ")":
                token = MToken(
                    RPAREN, RPAREN, self.cur_file, self.cur_line, self.cur_pos
                )
                self._n_paren -= 1
                if self._n_paren < 0:
                    self.errors.append(
                        MLexerError(token, "closing ')' was never opened")
                    )
                self._last_paren = token
            case "{":
                token = MToken(
                    LBRACE, LBRACE, self.cur_file, self.cur_line, self.cur_pos
                )
                self._n_braces += 1
                self._last_brace = token
            case "}":
                token = MToken(
                    RBRACE, RBRACE, self.cur_file, self.cur_line, self.cur_pos
                )
                self._n_braces -= 1
                if self._n_braces < 0:
                    self.errors.append(
                        MLexerError(token, "closing '}' was never opened")
                    )
                self._last_brace = token
            case "[":
                token = MToken(
                    LBRACKET, LBRACKET, self.cur_file, self.cur_line, self.cur_pos
                )
                self._n_brackets += 1
                self._last_bracket = token
            case "]":
                token = MToken(
                    RBRACKET, RBRACKET, self.cur_file, self.cur_line, self.cur_pos
                )
                self._n_brackets -= 1
                if self._n_brackets < 0:
                    self.errors.append(
                        MLexerError(token, "closing ']' was never opened")
                    )
                self._last_bracket = token

            case "\0":
                raise StopIteration

            case _:
                if self._ch.isalpha():
                    pos = self._position
                    while self._ch.isalpha():
                        self._read_ch()
                    identifier = self._input[pos : self._position]
                    if identifier in keywords:
                        return MToken(
                            KEYWORD,
                            identifier,
                            self.cur_file,
                            self.cur_line,
                            self.cur_pos,
                        )
                    else:
                        return MToken(
                            IDENTIFIER,
                            identifier,
                            self.cur_file,
                            self.cur_line,
                            self.cur_pos,
                        )

                elif self._ch.isnumeric():
                    pos = self._position
                    while self._ch.isnumeric():
                        self._read_ch()
                    number = self._input[pos : self._position]
                    return MToken(
                        NUMBER,
                        number,
                        self.cur_file,
                        self.cur_line,
                        self.cur_pos,
                    )

                else:
                    token = MToken(
                        ILLEGAL,
                        ILLEGAL,
                        self.cur_file,
                        self.cur_line,
                        self.cur_pos,
                    )

        self._read_ch()
        return token

    def _read_string(self) -> str:
        pos = self._position + 1
        while True:
            self._read_ch()
            if self._ch == '"' or self._ch == "\0":
                break
        return self._input[pos : self._position]

    def _read_ch(self):
        try:
            self._ch = self._input[self._read_position]
        except IndexError:
            if self._n_braces > 0:
                self.errors.append(
                    MLexerError(self._last_brace, "opening '{' was never closed")
                )
            if self._n_paren > 0:
                self.errors.append(
                    MLexerError(self._last_paren, "opening '(' was never closed")
                )
            if self._n_brackets > 0:
                self.errors.append(
                    MLexerError(self._last_bracket, "opening '[' was never closed")
                )
            self._ch = "\0"
        else:
            self._position = self._read_position
            self._read_position += 1
            self.cur_pos += 1

    def _next_ch(self) -> str:
        try:
            return self._input[self._read_position]
        except IndexError:
            if self._n_braces > 0:
                self.errors.append(
                    MLexerError(self._last_brace, "opening '{' was never closed")
                )
            if self._n_paren > 0:
                self.errors.append(
                    MLexerError(self._last_paren, "opening '(' was never closed")
                )
            if self._n_brackets > 0:
                self.errors.append(
                    MLexerError(self._last_bracket, "opening '[' was never closed")
                )
            return "\0"
