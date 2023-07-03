from dataclasses import dataclass

from pymonkey.lexer.mtoken import KEYWORDS, MToken, MTokenPosition, MTokenType


@dataclass
class MLexerError:
    token: MToken
    msg: str


class MLexer:
    def __init__(self, code: str, file_name: str = "test") -> None:
        self._input = code
        self._position = 0
        self._read_position = 0
        self._ch = ""
        self._token_position = MTokenPosition(file_name, 0, 0)

        self.errors: list[MLexerError] = []

        self._n_braces = 0
        self._n_paren = 0
        self._n_brackets = 0
        self._last_brace = MToken()
        self._last_paren = MToken()
        self._last_bracket = MToken()

        self._read_ch()

    def __iter__(self) -> "MLexer":
        return self

    def __next__(self) -> MToken:
        """
        Return next MToken
        """
        while self._ch.isspace():
            if self._ch == "\n":
                self._token_position.line += 1
                self._token_position.pos = 0
            self._read_ch()

        token: MToken
        match self._ch:
            case "=":
                if self._next_ch() == "=":
                    self._read_ch()
                    token = MToken(MTokenType.Equal, "==", self._token_position)
                else:
                    token = MToken(MTokenType.Assign, "=", self._token_position)
            case "+":
                token = MToken(MTokenType.Plus, "+", self._token_position)
            case "-":
                token = MToken(MTokenType.Minus, "-", self._token_position)
            case "!":
                if self._next_ch() == "=":
                    self._read_ch()
                    token = MToken(MTokenType.NotEqual, "!=", self._token_position)
                else:
                    token = MToken(MTokenType.Bang, "!", self._token_position)
            case "*":
                token = MToken(MTokenType.Asterisk, "*", self._token_position)
            case "/":
                token = MToken(MTokenType.Slash, "/", self._token_position)
            case "<":
                token = MToken(MTokenType.Lesser, "<", self._token_position)
            case ">":
                token = MToken(MTokenType.Greater, ">", self._token_position)

            case ",":
                token = MToken(MTokenType.Comma, ",", self._token_position)
            case ";":
                token = MToken(MTokenType.Semicolon, ";", self._token_position)
            case ":":
                token = MToken(MTokenType.Colon, ":", self._token_position)
            case '"':
                token = MToken(
                    MTokenType.String, self._read_string(), self._token_position
                )
            case "(":
                token = MToken(MTokenType.LParen, "(", self._token_position)
                self._n_paren += 1
                self._last_paren = token
            case ")":
                token = MToken(MTokenType.RParen, ")", self._token_position)
                self._n_paren -= 1
                if self._n_paren < 0:
                    self.errors.append(
                        MLexerError(token, "closing ')' was never opened")
                    )
                self._last_paren = token
            case "{":
                token = MToken(MTokenType.LBrace, "{", self._token_position)
                self._n_braces += 1
                self._last_brace = token
            case "}":
                token = MToken(MTokenType.RBrace, "}", self._token_position)
                self._n_braces -= 1
                if self._n_braces < 0:
                    self.errors.append(
                        MLexerError(token, "closing '}' was never opened")
                    )
                self._last_brace = token
            case "[":
                token = MToken(MTokenType.LBracket, "[", self._token_position)
                self._n_brackets += 1
                self._last_bracket = token
            case "]":
                token = MToken(MTokenType.RBracket, "]", self._token_position)
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
                            MTokenType.Keyword, identifier, self._token_position
                        )
                    else:
                        return MToken(
                            MTokenType.Identifier, identifier, self._token_position
                        )

                elif self._ch.isnumeric():
                    pos = self._position
                    while self._ch.isnumeric():
                        self._read_ch()
                    number = self._input[pos : self._position]
                    return MToken(MTokenType.Number, number, self._token_position)

                else:
                    token = MToken()

        self._read_ch()
        return token

    def _read_string(self) -> str:
        """
        Read String from one " to next " or EOF
        """
        pos = self._position + 1
        while True:
            self._read_ch()
            if self._ch == '"' or self._ch == "\0":
                break
        return self._input[pos : self._position]

    def _read_ch(self) -> None:
        """
        Advance Lexer by one character
        """
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
        """
        Peek next character without advancing the Lexer
        """
        try:
            return self._input[self._read_position]
        except IndexError:
            return "\0"
