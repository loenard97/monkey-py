from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List

from pymonkey.lexer.mlexer import MLexer
from pymonkey.lexer.mtoken import MToken, MTokenPosition, MTokenType
from pymonkey.parser.mast import (
    MArrayExpression,
    MBlockStatement,
    MBooleanExpression,
    MCallExpression,
    MExpression,
    MExpressionStatement,
    MFunctionExpression,
    MHashMapExpression,
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
        if token.type == MTokenType.Equal or token.type == MTokenType.NotEqual:
            return cls.Equals
        if token.type == MTokenType.Lesser or token.type == MTokenType.Greater:
            return cls.Comparison
        if token.type == MTokenType.Plus or token.type == MTokenType.Minus:
            return cls.Sum
        if token.type == MTokenType.Asterisk or token.type == MTokenType.Slash:
            return cls.Product
        if token.type == MTokenType.LParen:
            return cls.Call
        if token.type == MTokenType.LBracket:
            return cls.Index
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
        self.cur_token = MToken()
        self.peek_token = MToken()

        self.next_token()
        self.next_token()

    def __str__(self):
        return f"Parser <{self.cur_token}>"

    def _record_error(self, msg: str):
        self.errors.append(ParserError(self.cur_token, msg))

    def prefix_parse_fn(self, token: MToken) -> Callable:
        if token.type == MTokenType.Identifier:
            return self.parse_identifier
        if token.type == MTokenType.Number:
            return self.parse_integer_literal
        if token.type == MTokenType.String:
            return self.parse_string_literal
        if token.type == MTokenType.Bang or token.type == MTokenType.Minus:
            return self.parse_prefix_expression
        if token.type == MTokenType.Keyword and (
            token.literal == "true" or token.literal == "false"
        ):
            return self.parse_boolean
        if token.type == MTokenType.LParen:
            return self.parse_grouped_expression
        if token.type == MTokenType.LBracket:
            return self.parse_array_literal
        if token.type == MTokenType.LBrace:
            return self.parse_hash_literal
        if token.type == MTokenType.Keyword and token.literal == "if":
            return self.parse_if_expression
        if token.type == MTokenType.Keyword and token.literal == "fn":
            return self.parse_function_literal
        self._record_error("unknown prefix")
        raise UnknownTokenException()

    def infix_parse_fn(self, token: MToken):
        match token.type, token.literal:
            case (
                MTokenType.Plus
                | MTokenType.Minus
                | MTokenType.Slash
                | MTokenType.Asterisk
                | MTokenType.Equal
                | MTokenType.NotEqual
                | MTokenType.Lesser
                | MTokenType.Greater,
                _,
            ):
                return self.parse_infix_expression

            case MTokenType.LParen, _:
                return self.parse_call_expression

            case MTokenType.LBracket, _:
                return self.parse_index_expression

            case _:
                return None

    def next_token(self):
        self.cur_token = self.peek_token
        try:
            self.peek_token = next(self.lexer)
        except StopIteration:
            self.peek_token = MToken(MTokenType.Eof, "EOF", MTokenPosition("", 0, 0))

    def expect_peek(self, token_type: MTokenType) -> bool:
        if self.peek_token.type == token_type:
            self.next_token()
            return True
        return False

    def parse_program(self) -> MProgram:
        statements = []

        while self.cur_token.type != MTokenType.Eof:
            statements.append(self.parse_statement())
            self.next_token()

        return MProgram(statements)

    def parse_identifier(self) -> MExpression:
        token = self.cur_token
        value = token.literal

        return MIdentifier(value, token)

    def parse_statement(self) -> MStatement:
        match self.cur_token.type, self.cur_token.literal:
            case MTokenType.Keyword, "let":
                return self.parse_let_statement()
            case MTokenType.Keyword, "return":
                return self.parse_return_statement()
            case _:
                return self.parse_expression_statement()

    def parse_let_statement(self) -> MStatement:
        if (
            self.cur_token.type != MTokenType.Keyword
            and self.cur_token.literal != "let"
        ):
            self._record_error("expected keyword let")
        token = self.cur_token

        self.next_token()

        name = MIdentifier(self.cur_token.literal, self.cur_token)

        if not self.expect_peek(MTokenType.Assign):
            self._record_error("expected '='")

        self.next_token()

        value = self.parse_expression(Precedence.Lowest)
        if value is None:
            self._record_error("let statement has no expression")
            raise UnknownTokenException()

        if self.peek_token.type == MTokenType.Semicolon:
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

        if self.peek_token.type == MTokenType.Semicolon:
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

        if self.peek_token.type == MTokenType.Semicolon:
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
        elements = self.parse_expression_list(MTokenType.RBracket)
        return MArrayExpression(elements, token)

    def parse_expression_list(self, end_token: MTokenType) -> List[MExpression]:
        expr_list: List[MExpression] = []

        if self.peek_token.type == end_token:
            self.next_token()
            return expr_list

        self.next_token()
        expr = self.parse_expression(Precedence.Lowest)
        if expr is not None:
            expr_list.append(expr)

        while self.peek_token.type == MTokenType.Comma:
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

        while self.peek_token.type != MTokenType.RBrace:
            self.next_token()
            key = self.parse_expression(Precedence.Lowest)
            if not isinstance(key, MValuedExpression):
                raise UnknownTokenException("not a hashable type")

            if not self.expect_peek(MTokenType.Colon):
                raise UnknownTokenException()

            self.next_token()

            value = self.parse_expression(Precedence.Lowest)
            if value is None:
                raise UnknownTokenException("not a value")

            pairs[key] = value

            if self.peek_token.type != MTokenType.RBrace and not self.expect_peek(
                MTokenType.Comma
            ):
                raise UnknownTokenException()

        if not self.expect_peek(MTokenType.RBrace):
            raise UnknownTokenException()

        return MHashMapExpression(pairs, token)

    def parse_grouped_expression(self) -> MExpression:
        self.next_token()

        expression = self.parse_expression(Precedence.Lowest)
        if expression is None:
            self._record_error("grouped expression has no expression")
            raise UnknownTokenException(
                f"grouped expr has no expr, token {self.cur_token}"
            )

        if not self.expect_peek(MTokenType.RParen):
            self._record_error("expected ')'")
            raise UnknownTokenException(f"expected ), got token {self.cur_token}")

        return expression

    def parse_if_expression(self) -> MExpression:
        token = self.cur_token

        if not self.expect_peek(MTokenType.LParen):
            self._record_error("expected '('")
            raise UnknownTokenException(f"expected (, got token {self.cur_token}")

        self.next_token()

        condition = self.parse_expression(Precedence.Lowest)
        if condition is None:
            self._record_error("if statement has no condition")
            raise UnknownTokenException(f"if has no condition, token {self.cur_token}")

        if not self.expect_peek(MTokenType.RParen):
            self._record_error("expected ')'")
            raise UnknownTokenException(f"expexted ), got token {self.cur_token}")

        if not self.expect_peek(MTokenType.LBrace):
            self._record_error("expected '{'")
            raise UnknownTokenException(f"expected {{, got token {self.cur_token}")

        consequence = self.parse_block_statement()

        if (
            self.peek_token.type == MTokenType.Keyword
            and self.peek_token.literal == "else"
        ):
            self.next_token()

            if not self.expect_peek(MTokenType.LBrace):
                self._record_error("expected '{'")
                raise UnknownTokenException(f"expected {{, got token {self.cur_token}")

            alternative = self.parse_block_statement()

        else:
            alternative = None

        return MIfExpression(condition, consequence, alternative, token)

    def parse_function_literal(self) -> MExpression:
        token = self.cur_token

        if not self.expect_peek(MTokenType.LParen):
            self._record_error("expected '('")
            raise UnknownTokenException(f"expected (, got token {self.cur_token}")

        parameters = self.parse_function_parameters()

        if not self.expect_peek(MTokenType.LBrace):
            self._record_error("expected '{'")
            raise UnknownTokenException(f"expected {{, got token {self.cur_token}")

        body = self.parse_block_statement()

        return MFunctionExpression(parameters, body, token)

    def parse_function_parameters(self) -> List[MExpression]:
        identifier: List[MExpression] = []

        if self.peek_token.type == MTokenType.RParen:
            self.next_token()
            return identifier

        self.next_token()

        token = self.cur_token
        value = token.literal
        ident = MIdentifier(value, token)

        identifier.append(ident)

        while self.peek_token.type == MTokenType.Comma:
            self.next_token()
            self.next_token()

            token = self.cur_token
            value = token.literal
            ident = MIdentifier(value, token)

            identifier.append(ident)

        if not self.expect_peek(MTokenType.RParen):
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

        if self.peek_token.type == MTokenType.RParen:
            self.next_token()
            return args

        self.next_token()

        arg = self.parse_expression(Precedence.Lowest)
        if arg is None:
            self._record_error("no call expression given")
            raise UnknownTokenException(f"call arg is none, token {self.cur_token}")
        args.append(arg)

        while self.peek_token.type == MTokenType.Comma:
            self.next_token()
            self.next_token()

            arg = self.parse_expression(Precedence.Lowest)
            if arg is None:
                self._record_error("call arg is none")
                raise UnknownTokenException(f"call arg is none token {self.cur_token}")
            args.append(arg)

        if not self.expect_peek(MTokenType.RParen):
            self._record_error("expected }")
            raise UnknownTokenException(f"expected }}, got token {self.cur_token}")

        return args

    def parse_index_expression(self, left: MExpression) -> MExpression:
        token = self.cur_token

        self.next_token()

        index = self.parse_expression(Precedence.Lowest)
        if index is None:
            raise UnknownTokenException()

        if not self.expect_peek(MTokenType.RBracket):
            raise UnknownTokenException()

        return MIndexExpression(left, index, token)

    def parse_block_statement(self) -> MBlockStatement:
        token = self.cur_token
        statements = []

        self.next_token()

        while (
            self.cur_token.type != MTokenType.RBrace
            and self.cur_token.type != MTokenType.Eof
        ):
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
            self.peek_token.type != MTokenType.Semicolon
            and precedence.value < peek_precedence.value
        ):
            infix = self.infix_parse_fn(self.peek_token)
            if infix is None:
                return left
            self.next_token()
            left = infix(left)

        return left
