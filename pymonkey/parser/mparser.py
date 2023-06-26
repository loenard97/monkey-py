from dataclasses import dataclass
from enum import Enum, auto
from typing import List

from pymonkey.lexer.mlexer import MLexer
from pymonkey.lexer.mtoken import (
    ASSIGN,
    COLON,
    COMMA,
    ELSE,
    EOF,
    ILLEGAL,
    LBRACE,
    LET,
    LPAREN,
    RBRACE,
    RBRACKET,
    RPAREN,
    SEMICOLON,
    MToken,
)
from pymonkey.parser.mast import (
    MArrayExpression,
    MBlockStatement,
    MBooleanExpression,
    MCallExpression,
    MExpression,
    MExpressionStatement,
    MFunctionExpression,
    MHashExpression,
    MIdentifier,
    MIfExpression,
    MIndexExpression,
    MInfixExpression,
    MIntegerExpression,
    MLetStatement,
    MPrefixExpression,
    MProgram,
    MReturnStatement,
    MStatement,
    MStringExpression,
    MValuedExpression,
)


class UnknownTokenException(Exception):
    pass


class Precedence(Enum):
    Lowest = auto()
    Equals = auto()
    Comparison = auto()
    Sum = auto()
    Product = auto()
    Prefix = auto()
    Call = auto()
    Index = auto()

    @classmethod
    def from_token(cls, token: MToken):
        match token.type:
            case "==" | "!=":
                return cls.Equals
            case "<" | ">":
                return cls.Comparison
            case "+" | "-":
                return cls.Sum
            case "*" | "/":
                return cls.Product
            case "(":
                return cls.Call
            case "[":
                return cls.Index
            case _:
                return cls.Lowest


@dataclass
class ParserError:
    token: MToken
    msg: str

    def __str__(self):
        return f"Parser Error: {self.msg} @ {self.token}"


class MParser:
    def __init__(self, lexer: MLexer):
        self.lexer = lexer
        self.errors: List[ParserError] = []
        self.cur_token = MToken(ILLEGAL, ILLEGAL, "", 0, 0)
        self.peek_token = MToken(ILLEGAL, ILLEGAL, "", 0, 0)

        self.next_token()
        self.next_token()

    def __str__(self):
        return f"Parser <{self.cur_token}>"

    def _record_error(self, msg: str):
        self.errors.append(ParserError(self.cur_token, msg))

    def prefix_parse_fn(self, token: MToken):
        match token.type, token.literal:
            case "Identifier", _:
                return self.parse_identifier
            case "Number", _:
                return self.parse_integer_literal
            case "String", _:
                return self.parse_string_literal

            case "!" | "-", "!" | "-":
                return self.parse_prefix_expression

            case "Keyword", "true" | "false":
                return self.parse_boolean

            case "(", "(":
                return self.parse_grouped_expression

            case "[", "[":
                return self.parse_array_literal

            case "{", "{":
                return self.parse_hash_literal

            case "Keyword", "if":
                return self.parse_if_expression

            case "Keyword", "fn":
                return self.parse_function_literal

            case _:
                self._record_error("Unknown Prefix")
                raise UnknownTokenException()

    def infix_parse_fn(self, token: MToken):
        match token.type, token.literal:
            case "+" | "-" | "/" | "*" | "==" | "!=" | "<" | ">", _:
                return self.parse_infix_expression

            case "(", _:
                return self.parse_call_expression

            case "[", _:
                return self.parse_index_expression

            case _:
                return None

    def next_token(self):
        self.cur_token = self.peek_token
        try:
            self.peek_token = next(self.lexer)
        except StopIteration:
            self.peek_token = MToken(EOF, EOF, "", 0, 0)

    def expect_peek(self, token_type) -> bool:
        if self.peek_token == token_type:
            self.next_token()
            return True
        return False

    def parse_program(self) -> MProgram:
        statements = []

        while self.cur_token.type != EOF:
            statements.append(self.parse_statement())
            self.next_token()

        return MProgram(statements)

    def parse_identifier(self) -> MExpression:
        token = self.cur_token
        value = token.literal

        return MIdentifier(value, token)

    def parse_statement(self) -> MStatement:
        match self.cur_token.type, self.cur_token.literal:
            case "Keyword", "let":
                return self.parse_let_statement()
            case "Keyword", "return":
                return self.parse_return_statement()
            case _:
                return self.parse_expression_statement()

    def parse_let_statement(self) -> MStatement:
        if self.cur_token != LET:
            self._record_error("expected keyword let")
        token = self.cur_token

        self.next_token()

        name = MIdentifier(self.cur_token.literal, self.cur_token)

        if not self.expect_peek(ASSIGN):
            self._record_error("expected '='")

        self.next_token()

        value = self.parse_expression(Precedence.Lowest)
        if value is None:
            self._record_error("let statement has no expression")
            raise UnknownTokenException()

        if self.peek_token.type == SEMICOLON:
            self.next_token()

        return MLetStatement(name, value, token)

    def parse_return_statement(self) -> MStatement:
        token = self.cur_token
        self.next_token()

        value = self.parse_expression(Precedence.Lowest)
        if value is None:
            self._record_error("return statement has no expression")
            raise UnknownTokenException(
                f"return statement has no value, token {self.cur_token}"
            )

        if self.peek_token.type == SEMICOLON:
            self.next_token()

        return MReturnStatement(value, token)

    def parse_expression_statement(self) -> MStatement:
        token = self.cur_token

        expression = self.parse_expression(Precedence.Lowest)
        if expression is None:
            self._record_error("expression statement has no expression")
            raise UnknownTokenException(
                f"expr stmt has no value, token {self.cur_token}"
            )

        if self.peek_token.type == SEMICOLON:
            self.next_token()

        return MExpressionStatement(expression, token)

    def parse_integer_literal(self) -> MExpression:
        token = self.cur_token
        value = int(token.literal)
        return MIntegerExpression(value, token)

    def parse_string_literal(self) -> MExpression:
        return MStringExpression(self.cur_token.literal, self.cur_token)

    def parse_prefix_expression(self) -> MExpression:
        token = self.cur_token
        operator = token.literal

        self.next_token()

        right = self.parse_expression(Precedence.Prefix)
        if right is None:
            self._record_error("prefix expression has no expression")
            raise UnknownTokenException(
                f"prefix expr has no value, token {self.cur_token}"
            )

        return MPrefixExpression(operator, right, token)

    def parse_boolean(self) -> MExpression:
        token = self.cur_token
        value = self.cur_token.literal == "true"

        return MBooleanExpression(value, token)

    def parse_array_literal(self) -> MExpression:
        token = self.cur_token
        elements = self.parse_expression_list(RBRACKET)
        return MArrayExpression(elements, token)

    def parse_expression_list(self, end_token: str) -> List[MExpression]:
        expr_list: List[MExpression] = []

        if self.peek_token == end_token:
            self.next_token()
            return expr_list

        self.next_token()
        expr = self.parse_expression(Precedence.Lowest)
        if expr is not None:
            expr_list.append(expr)

        while self.peek_token == COMMA:
            self.next_token()
            self.next_token()
            expr = self.parse_expression(Precedence.Lowest)
            if expr is not None:
                expr_list.append(expr)

        if not self.expect_peek(end_token):
            raise UnknownTokenException("expected ]")

        return expr_list

    def parse_hash_literal(self) -> MExpression:
        token = self.cur_token
        pairs = dict()

        while self.peek_token != RBRACE:
            self.next_token()
            key = self.parse_expression(Precedence.Lowest)
            if not isinstance(key, MValuedExpression):
                raise UnknownTokenException("not a hashable type")

            if not self.expect_peek(COLON):
                raise UnknownTokenException()

            self.next_token()

            value = self.parse_expression(Precedence.Lowest)
            if value is None:
                raise UnknownTokenException("not a value")

            pairs[key] = value

            if self.peek_token != RBRACE and not self.expect_peek(COMMA):
                raise UnknownTokenException()

        if not self.expect_peek(RBRACE):
            raise UnknownTokenException()

        return MHashExpression(pairs, token)

    def parse_grouped_expression(self) -> MExpression:
        self.next_token()

        expression = self.parse_expression(Precedence.Lowest)
        if expression is None:
            self._record_error("grouped expression has no expression")
            raise UnknownTokenException(
                f"grouped expr has no expr, token {self.cur_token}"
            )

        if not self.expect_peek(RPAREN):
            self._record_error("expected ')'")
            raise UnknownTokenException(f"expected ), got token {self.cur_token}")

        return expression

    def parse_if_expression(self) -> MExpression:
        token = self.cur_token

        if not self.expect_peek(LPAREN):
            self._record_error("expected '('")
            raise UnknownTokenException(f"expected (, got token {self.cur_token}")

        self.next_token()

        condition = self.parse_expression(Precedence.Lowest)
        if condition is None:
            self._record_error("if statement has no condition")
            raise UnknownTokenException(f"if has no condition, token {self.cur_token}")

        if not self.expect_peek(RPAREN):
            self._record_error("expected ')'")
            raise UnknownTokenException(f"expexted ), got token {self.cur_token}")

        if not self.expect_peek(LBRACE):
            self._record_error("expected '{'")
            raise UnknownTokenException(f"expected {{, got token {self.cur_token}")

        consequence = self.parse_block_statement()

        if self.peek_token.literal == ELSE:
            self.next_token()

            if not self.expect_peek(LBRACE):
                self._record_error("expected '{'")
                raise UnknownTokenException(f"expected {{, got token {self.cur_token}")

            alternative = self.parse_block_statement()

        else:
            alternative = None

        return MIfExpression(condition, consequence, alternative, token)

    def parse_function_literal(self) -> MExpression:
        token = self.cur_token

        if not self.expect_peek(LPAREN):
            self._record_error("expected '('")
            raise UnknownTokenException(f"expected (, got token {self.cur_token}")

        parameters = self.parse_function_parameters()

        if not self.expect_peek(LBRACE):
            self._record_error("expected '{'")
            raise UnknownTokenException(f"expected {{, got token {self.cur_token}")

        body = self.parse_block_statement()

        return MFunctionExpression(parameters, body, token)

    def parse_function_parameters(self) -> List[MExpression]:
        identifier: List[MExpression] = []

        if self.peek_token.type == RPAREN:
            self.next_token()
            return identifier

        self.next_token()

        token = self.cur_token
        value = token.literal
        ident = MIdentifier(value, token)

        identifier.append(ident)

        while self.peek_token.type == COMMA:
            self.next_token()
            self.next_token()

            token = self.cur_token
            value = token.literal
            ident = MIdentifier(value, token)

            identifier.append(ident)

        if not self.expect_peek(RPAREN):
            self._record_error("expected '}}'")
            raise UnknownTokenException(f"expected }}, got token {self.cur_token}")

        return identifier

    def parse_infix_expression(self, left: MExpression) -> MExpression:
        token = self.cur_token
        operator = token.literal
        precedence = Precedence.from_token(token)

        self.next_token()

        right = self.parse_expression(precedence)
        if right is None:
            self._record_error("infix expression is missing right side expression")
            raise UnknownTokenException(f"infix right is none token {self.cur_token}")

        return MInfixExpression(operator, left, right, token)

    def parse_call_expression(self, function: MExpression) -> MExpression:
        token = self.cur_token
        arguments = self.parse_call_arguments()

        return MCallExpression(function, arguments, token)

    def parse_call_arguments(self) -> List[MExpression]:
        args: List[MExpression] = []

        if self.peek_token.type == RPAREN:
            self.next_token()
            return args

        self.next_token()

        arg = self.parse_expression(Precedence.Lowest)
        if arg is None:
            self._record_error("no call expression given")
            raise UnknownTokenException(f"call arg is none, token {self.cur_token}")
        args.append(arg)

        while self.peek_token.type == COMMA:
            self.next_token()
            self.next_token()

            arg = self.parse_expression(Precedence.Lowest)
            if arg is None:
                self._record_error("call arg is none")
                raise UnknownTokenException(f"call arg is none token {self.cur_token}")
            args.append(arg)

        if not self.expect_peek(RPAREN):
            self._record_error("expected }")
            raise UnknownTokenException(f"expected }}, got token {self.cur_token}")

        return args

    def parse_index_expression(self, left: MExpression) -> MExpression:
        token = self.cur_token

        self.next_token()

        index = self.parse_expression(Precedence.Lowest)
        if index is None:
            raise UnknownTokenException()

        if not self.expect_peek(RBRACKET):
            raise UnknownTokenException()

        return MIndexExpression(left, index, token)

    def parse_block_statement(self) -> MBlockStatement:
        token = self.cur_token
        statements = []

        self.next_token()

        while self.cur_token.type != RBRACE and self.cur_token.type != EOF:
            stmt = self.parse_statement()
            statements.append(stmt)
            self.next_token()

        return MBlockStatement(statements, token)

    def parse_expression(self, precedence: Precedence) -> MExpression | None:
        token = self.cur_token

        left = None
        try:
            left = self.prefix_parse_fn(token)()
        except UnknownTokenException:
            return None

        peek_precedence = Precedence.from_token(self.peek_token)

        while (
            self.peek_token.type != SEMICOLON
            and precedence.value < peek_precedence.value
        ):
            infix = self.infix_parse_fn(self.peek_token)
            if infix is None:
                return left
            self.next_token()
            left = infix(left)

        return left