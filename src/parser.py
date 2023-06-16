from enum import Enum, auto

from .ast import *
from .token import *
from .lexer import *


class UnknownTokenException(Exception):
    pass


class Precedence(Enum):

    Lowest      = auto()
    Equals      = auto()
    Comparison  = auto()
    Sum         = auto()
    Product     = auto()
    Prefix      = auto()
    Call        = auto()

    @classmethod
    def from_token(cls, token: Token):
        match token.type:
            case "==":
                return cls.Equals
            case _:
                return cls.Lowest


class Parser:

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.errors = []
        self.cur_token = Token(ILLEGAL, ILLEGAL)
        self.peek_token = Token(ILLEGAL, ILLEGAL)

        self.prefix_parse_fn = {
            IDENTIFIER: self.parse_identifier,
            NUMBER:     self.parse_integer_literal,

            BANG:       self.parse_prefix_expression,
            MINUS:      self.parse_prefix_expression,

            TRUE:       self.parse_boolean,
            FALSE:      self.parse_boolean,

            LPAREN:     self.parse_grouped_expression,

            IF:         self.parse_if_expression,
            FUNCTION:   self.parse_function_literal,
        }

        self.infix_parse_fn = {
            PLUS:       self.parse_infix_expression,
            MINUS:      self.parse_infix_expression,
            SLASH:      self.parse_infix_expression,
            ASTERISK:   self.parse_infix_expression,
            EQUAL:      self.parse_infix_expression,
            NOTEQUAL:   self.parse_infix_expression,
            LESSER:     self.parse_infix_expression,
            GREATER:    self.parse_infix_expression,

            LPAREN:     self.parse_call_expression,
        }

        self.next_token()
        self.next_token()

    def next_token(self):
        self.cur_token = self.peek_token
        try:
            self.peek_token = next(self.lexer)
        except StopIteration:
            self.peek_token = Token(EOF, EOF)

    def expect_peek(self, token_type) -> bool:
        if self.next_token.type == token_type:
            self.next_token()
            return True
        return False

    def parse_program(self) -> Program:
        statements = []

        while self.cur_token.type != EOF:
            statements.append(self.parse_statement())
            self.next_token()

        return Program(statements)

    def parse_identifier(self) -> Expression:
        token = self.cur_token
        value = token.literal

        return Identifier(token, value)

    def parse_statement(self) -> Statement:
        match self.cur_token.type:
            case "let":
                return self.parse_let_statement()
            case "return":
                return self.parse_return_statement()
            case _:
                return self.parse_expression_statement()

    def parse_let_statement(self) -> Statement:
        if self.cur_token.type != LET:
            raise UnknownTokenException
        token = self.cur_token

        self.next_token()

        name = Identifier(self.cur_token, self.cur_token.literal)

        if not self.expect_peek(ASSIGN):
            raise UnknownTokenException

        self.next_token()

        value = self.parse_expression(Precedence.Lowest)

        if self.peek_token.type == SEMICOLON:
            self.next_token()

        return LetStatement(token, name, value)

    def parse_return_statement(self) -> Statement:
        token = self.cur_token
        self.next_token()

        value = self.parse_expression(Precedence.Lowest)

        if self.peek_token.type == SEMICOLON:
            self.next_token()

        return ReturnStatement(token, value)

    def parse_expression_statement(self) -> Statement:
        token = self.cur_token

        expression = self.parse_expression(Precedence.Lowest)

        if self.peek_token.type == SEMICOLON:
            self.next_token()

        return ExpressionStatement(token, expression)

    def parse_integer_literal(self) -> Expression:
        token = self.cur_token
        value = int(token.literal)
        return Integer(token, value)

    def parse_prefix_expression(self) -> Expression:
        token = self.cur_token
        operator = token.literal

        self.next_token()

        right = self.parse_expression(Precedence.Prefix)

        return Prefix(token, operator, right)

    def parse_boolean(self) -> Expression:
        token = self.cur_token
        value = self.cur_token.literal == "true"

        return Boolean(token, value)

    def parse_grouped_expression(self) -> Expression:
        self.next_token()

        expression = self.parse_expression(Precedence.Lowest)

        if self.peek_token.type != LPAREN:
            raise UnknownTokenException

        return expression

    def parse_if_expression(self) -> Expression:
        token = self.cur_token

        if not self.expect_peek(LPAREN):
            raise UnknownTokenException

        self.next_token()

        condition = self.parse_expression(Precedence.Lowest)

        if not self.expect_peek(RPAREN):
            raise UnknownTokenException

        if not self.expect_peek(RBRACE):
            raise UnknownTokenException

        consequence = self.parse_block_statement()

        if self.peek_token.type == ELSE:
            self.next_token()

            if not self.expect_peek(LBRACE):
                raise UnknownTokenException

            alternative = self.parse_block_statement()

        else:
            alternative = EmptyStatement()

        return If(token, condition, consequence, alternative)

    def parse_function_literal(self) -> Expression:
        token = self.cur_token

        if not self.expect_peek(LPAREN):
            raise UnknownTokenException

        parameters = self.parse_function_parameters()

        if not self.expect_peek(LBRACE):
            raise UnknownTokenException

        body = self.parse_block_statement()

        return Function(token, parameters, body)

    def parse_function_parameters(self) -> List[Expression]:
        identifier = []

        if self.peek_token.type == RPAREN:
            self.next_token()
            return identifier

        self.next_token()

        token = self.cur_token
        value = token.literal
        ident = Identifier(token, value)

        identifier.append(ident)

        if self.peek_token == COMMA:
            self.next_token()
            self.next_token()

            token = self.cur_token
            value = token.literal
            ident = Identifier(token, value)

            identifier.append(ident)

        if self.expect_peek(RPAREN):
            raise UnknownTokenException

        return identifier

    def parse_infix_expression(self, left: Expression) -> Expression:
        token = self.cur_token
        operator = token.literal
        precedence = Precedence.from_token(token)

        self.next_token()

        right = self.parse_expression(precedence)

        return Infix(token, operator, left, right)

    def parse_call_expression(self, function: Expression) -> Expression:
        token = self.cur_token
        arguments = self.parse_call_arguments()

        return Call(token, function, arguments)

    def parse_call_arguments(self) -> List[Expression]:
        args = []

        if self.peek_token.type == RPAREN:
            self.next_token()
            return args

        self.next_token()
        args.append(self.parse_expression(Precedence.Lowest))

        while self.peek_token.type == COMMA:
            self.next_token()
            self.next_token()

            args.append(self.parse_expression(Precedence.Lowest))

            if not self.expect_peek(RPAREN):
                raise UnknownTokenException

        return args

    def parse_block_statement(self) -> BlockStatement:
        token = self.cur_token
        statemtens = []

        self.next_token()

        if token.type != RBRACE and token.type != EOF:
            stmt = self.parse_statement()
            statemtens.append(stmt)
            self.next_token()

        return BlockStatement(token, statemtens)

    def parse_expression(self, precedence: Precedence) -> Expression:
        token = self.cur_token

        left = EmptyExpression()
        left_fn = self.prefix_parse_fn[token.type]

        peek_precedence = Precedence.from_token(self.peek_token)

        while self.peek_token.type != SEMICOLON and precedence.value < peek_precedence.value:
            infix_fn = self.infix_parse_fn[self.peek_token.type]
            self.next_token()
            left = infix_fn(self, left_fn)

        return left

