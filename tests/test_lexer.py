from pymonkey.token import *
from pymonkey.lexer import Lexer


def test_token():
    input = "=+(){},;-!/*<>"
    tokens = [
        Token(ASSIGN, ASSIGN),
        Token(PLUS, PLUS),
        Token(LPAREN, LPAREN),
        Token(RPAREN, RPAREN),
        Token(LBRACE, LBRACE),
        Token(RBRACE, RBRACE),
        Token(COMMA, COMMA),
        Token(SEMICOLON, SEMICOLON),
        Token(MINUS, MINUS),
        Token(BANG, BANG),
        Token(SLASH, SLASH),
        Token(ASTERISK, ASTERISK),
        Token(LESSER, LESSER),
        Token(GREATER, GREATER),
    ]

    run_lexer(input, tokens)


def test_composed_token():
    input = "0 == 0; 0 != 1;"
    tokens = [
        Token(NUMBER, "0"),
        Token(EQUAL, "=="),
        Token(NUMBER, "0"),
        Token(SEMICOLON, SEMICOLON),
        
        Token(NUMBER, "0"),
        Token(NOTEQUAL, "!="),
        Token(NUMBER, "1"),
        Token(SEMICOLON, SEMICOLON),
    ]

    run_lexer(input, tokens)


def run_lexer(input, tokens):
    lexer = Lexer(input)

    for lex_token, token in zip(lexer, tokens):
        print(f"{lex_token=} {token=}")
        assert lex_token == token

