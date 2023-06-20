from enum import Enum, auto

from pymonkey.ast import *
from pymonkey.token import *
from pymonkey.lexer import *

from pymonkey.util import flog


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
            case _:
                return cls.Lowest


class ParserError:
    pass


class Parser:

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.errors: List[ParserError] = []
        self.cur_token = Token(ILLEGAL, ILLEGAL)
        self.peek_token = Token(ILLEGAL, ILLEGAL)

        self.next_token()
        self.next_token()

    def __str__(self):
        return f"Parser <{self.cur_token}>"

    @flog
    def prefix_parse_fn(self, token: Token):
        match token.type, token.literal:
            case "Identifier", _:
                return self.parse_identifier
            case "Number", _:
                return self.parse_integer_literal

            case "!" | "-", "!" | "-":
                return self.parse_prefix_expression

            case "Keyword", "true" | "false":
                return self.parse_boolean

            case "(", "(":
                return self.parse_grouped_expression

            case "Keyword", "if":
                return self.parse_if_expression

            case "Keyword", "fn":
                return self.parse_function_literal

            case _:
                raise UnknownTokenException

    @flog
    def infix_parse_fn(self, token: Token):
        print(f"infix {token.type} {token.literal}")
        match token.type, token.literal:
            case "+" | "-" | "/" | "*" | "==" | "!=" | "<" | ">", _:
                return self.parse_infix_expression

            case "(", _:
                return self.parse_call_expression

            case _:
                return None

    @flog
    def next_token(self):
        self.cur_token = self.peek_token
        try:
            self.peek_token = next(self.lexer)
        except StopIteration:
            self.peek_token = Token(EOF, EOF)

    @flog
    def expect_peek(self, token_type) -> bool:
        if self.peek_token == token_type:
            self.next_token()
            return True
        return False


    @flog
    def parse_program(self) -> Program:
        statements = []

        while self.cur_token.type != EOF:
            statements.append(self.parse_statement())
            self.next_token()

        return Program(statements)

    @flog
    def parse_identifier(self) -> Expression:
        token = self.cur_token
        value = token.literal

        return Identifier(value, token)

    @flog
    def parse_statement(self) -> Statement:
        match self.cur_token.type, self.cur_token.literal:
            case "Keyword", "let":
                return self.parse_let_statement()
            case "Keyword", "return":
                return self.parse_return_statement()
            case _:
                return self.parse_expression_statement()

    @flog
    def parse_let_statement(self) -> Statement:
        if self.cur_token != LET:
            raise UnknownTokenException
        token = self.cur_token

        self.next_token()

        name = Identifier(self.cur_token.literal, self.cur_token)

        if not self.expect_peek(ASSIGN):
            raise UnknownTokenException

        self.next_token()

        value = self.parse_expression(Precedence.Lowest)
        if value is None:
            raise UnknownTokenException

        if self.peek_token.type == SEMICOLON:
            self.next_token()

        return LetStatement(name, value, token)

    @flog
    def parse_return_statement(self) -> Statement:
        token = self.cur_token
        self.next_token()

        value = self.parse_expression(Precedence.Lowest)
        if value is None:
            raise UnknownTokenException

        if self.peek_token.type == SEMICOLON:
            self.next_token()

        return ReturnStatement(value, token)

    @flog
    def parse_expression_statement(self) -> Statement:
        token = self.cur_token

        expression = self.parse_expression(Precedence.Lowest)
        if expression is None:
            raise UnknownTokenException

        if self.peek_token.type == SEMICOLON:
            self.next_token()

        return ExpressionStatement(expression, token)

    @flog
    def parse_integer_literal(self) -> Expression:
        token = self.cur_token
        value = int(token.literal)
        return IntegerExpression(value, token)

    @flog
    def parse_prefix_expression(self) -> Expression:
        token = self.cur_token
        operator = token.literal

        self.next_token()

        right = self.parse_expression(Precedence.Prefix)
        if right is None:
            raise UnknownTokenException

        return PrefixExpression(operator, right, token)

    @flog
    def parse_boolean(self) -> Expression:
        token = self.cur_token
        value = self.cur_token.literal == "true"

        return BooleanExpression(value, token)

    @flog
    def parse_grouped_expression(self) -> Expression:
        self.next_token()

        expression = self.parse_expression(Precedence.Lowest)
        print(f"group {expression}")
        if expression is None:
            raise UnknownTokenException

        if not self.expect_peek(RPAREN):
            raise UnknownTokenException

        return expression

    @flog
    def parse_if_expression(self) -> Expression:
        token = self.cur_token

        if not self.expect_peek(LPAREN):
            raise UnknownTokenException

        self.next_token()

        condition = self.parse_expression(Precedence.Lowest)
        if condition is None:
            raise UnknownTokenException

        if not self.expect_peek(RPAREN):
            raise UnknownTokenException

        if not self.expect_peek(LBRACE):
            raise UnknownTokenException

        consequence = self.parse_block_statement()

        if self.peek_token.literal == ELSE:
            self.next_token()

            if not self.expect_peek(LBRACE):
                raise UnknownTokenException

            alternative = self.parse_block_statement()

        else:
            alternative = None

        return IfExpression(condition, consequence, alternative, token)

    @flog
    def parse_function_literal(self) -> Expression:
        token = self.cur_token

        
        if not self.expect_peek(LPAREN):
            raise UnknownTokenException

        parameters = self.parse_function_parameters()

        if not self.expect_peek(LBRACE):
            raise UnknownTokenException

        body = self.parse_block_statement()

        return FunctionExpression(parameters, body, token)

    @flog
    def parse_function_parameters(self) -> List[Expression]:
        identifier: List[Expression] = []

        if self.peek_token.type == RPAREN:
            self.next_token()
            return identifier

        self.next_token()

        token = self.cur_token
        value = token.literal
        ident = Identifier(value, token)

        identifier.append(ident)

        while self.peek_token.type == COMMA:
            self.next_token()
            self.next_token()

            token = self.cur_token
            value = token.literal
            ident = Identifier(value, token)

            identifier.append(ident)

        if not self.expect_peek(RPAREN):
            raise UnknownTokenException

        return identifier

    @flog
    def parse_infix_expression(self, left: Expression) -> Expression:
        token = self.cur_token
        operator = token.literal
        precedence = Precedence.from_token(token)

        self.next_token()

        print("parse expr")
        right = self.parse_expression(precedence)
        if right is None:
            print("right is none")
            print(left)
            print(precedence)
            raise UnknownTokenException

        return InfixExpression(operator, left, right, token)

    @flog
    def parse_call_expression(self, function: Expression) -> Expression:
        token = self.cur_token
        arguments = self.parse_call_arguments()

        return CallExpression(function, arguments, token)

    @flog
    def parse_call_arguments(self) -> List[Expression]:
        args: List[Expression] = []

        if self.peek_token.type == RPAREN:
            self.next_token()
            return args

        self.next_token()

        arg = self.parse_expression(Precedence.Lowest)
        if arg is None:
            raise UnknownTokenException
        args.append(arg)

        while self.peek_token.type == COMMA:
            self.next_token()
            self.next_token()

            arg = self.parse_expression(Precedence.Lowest)
            if arg is None:
                raise UnknownTokenException
            args.append(arg)

        if not self.expect_peek(RPAREN):
            raise UnknownTokenException

        return args

    @flog
    def parse_block_statement(self) -> BlockStatement:
        token = self.cur_token
        statemtens = []

        self.next_token()

        if token.type != RBRACE and token.type != EOF:
            stmt = self.parse_statement()
            statemtens.append(stmt)
            self.next_token()

        return BlockStatement(statemtens, token)

    @flog
    def parse_expression(self, precedence: Precedence) -> Expression | None:
        token = self.cur_token

        left = None
        try:
            left = self.prefix_parse_fn(token)()
        except UnknownTokenException:
            return None

        peek_precedence = Precedence.from_token(self.peek_token)

        while self.peek_token.type != SEMICOLON and precedence.value < peek_precedence.value:
            print("while")
            infix = self.infix_parse_fn(self.peek_token)
            if infix is None:
                print(f"infix is None return {left}")
                return left
            self.next_token()
            left = infix(left)

        return left

