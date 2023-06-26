from dataclasses import dataclass
from typing import List

from pymonkey.lexer.mtoken import KEYWORDS, MToken, TokenPosition, TokenType


@dataclass
class MLexerError:
    token: MToken
    msg: str


class MLexer:
    def __init__(self, input, file_name):
        self._input = input
        self._position = 0
        self._read_position = 0
        self._ch = ""
        self._token_position = TokenPosition(file_name, 0, 0)

        self.errors: List[MLexerError] = []

        self._n_braces = 0
        self._n_paren = 0
        self._n_brackets = 0
        self._last_brace = MToken()
        self._last_paren = MToken()
        self._last_bracket = MToken()

        self._read_ch()

    def __iter__(self):
        return self

    def __next__(self) -> MToken:
        while self._ch.isspace():
            if self._ch == "\n":
                self._token_position.line += 1
                self._token_position.pos = 0
            self._read_ch()

        token = MToken()
        match self._ch:
            case "=":
                if self._next_ch() == "=":
                    self._read_ch()
                    token = MToken(TokenType.Equal, "==", self._token_position)
                else:
                    token = MToken(TokenType.Assign, "=", self._token_position)
            case "+":
                token = MToken(TokenType.Plus, "+", self._token_position)
            case "-":
                token = MToken(TokenType.Minus, "-", self._token_position)
            case "!":
                if self._next_ch() == "=":
                    self._read_ch()
                    token = MToken(TokenType.NotEqual, "!=", self._token_position)
                else:
                    token = MToken(TokenType.Bang, "!", self._token_position)
            case "*":
                token = MToken(TokenType.Asterisk, "*", self._token_position)
            case "/":
                token = MToken(TokenType.Slash, "/", self._token_position)
            case "<":
                token = MToken(TokenType.Lesser, "<", self._token_position)
            case ">":
                token = MToken(TokenType.Greater, ">", self._token_position)

            case ",":
                token = MToken(TokenType.Comma, ",", self._token_position)
            case ";":
                token = MToken(TokenType.Semicolon, ";", self._token_position)
            case ":":
                token = MToken(TokenType.Colon, ":", self._token_position)
            case '"':
                token = MToken(
                    TokenType.String, self._read_string(), self._token_position
                )
            case "(":
                token = MToken(TokenType.LParen, "(", self._token_position)
                self._n_paren += 1
                self._last_paren = token
            case ")":
                token = MToken(TokenType.RParen, ")", self._token_position)
                self._n_paren -= 1
                if self._n_paren < 0:
                    self.errors.append(
                        MLexerError(token, "closing ')' was never opened")
                    )
                self._last_paren = token
            case "{":
                token = MToken(TokenType.LBrace, "{", self._token_position)
                self._n_braces += 1
                self._last_brace = token
            case "}":
                token = MToken(TokenType.RBrace, "}", self._token_position)
                self._n_braces -= 1
                if self._n_braces < 0:
                    self.errors.append(
                        MLexerError(token, "closing '}' was never opened")
                    )
                self._last_brace = token
            case "[":
                token = MToken(TokenType.LBracket, "[", self._token_position)
                self._n_brackets += 1
                self._last_bracket = token
            case "]":
                token = MToken(TokenType.RBracket, "]", self._token_position)
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
                    if identifier in KEYWORDS:
                        return MToken(
                            TokenType.Keyword, identifier, self._token_position
                        )
                    else:
                        return MToken(
                            TokenType.Identifier, identifier, self._token_position
                        )

                elif self._ch.isnumeric():
                    pos = self._position
                    while self._ch.isnumeric():
                        self._read_ch()
                    number = self._input[pos : self._position]
                    return MToken(TokenType.Number, number, self._token_position)

                else:
                    token = MToken()

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
            self._token_position.pos += 1

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
